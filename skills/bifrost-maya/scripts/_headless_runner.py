"""Runs inside mayapy for bifrost_headless.py. Not meant to be called directly.

argv: spec.json result.json. Builds the graph from the spec with the vnn
commands, reads the requested outputs and writes a JSON report.
"""
import io
import json
import os
import sys
import time
import traceback

spec_path, result_path = sys.argv[1], sys.argv[2]
with open(spec_path, encoding="utf-8") as stream:
    specs = json.load(stream)
single = isinstance(specs, dict)
if single:
    specs = [specs]

session = {"graphs": [], "timing": {}}
report = None
SCALAR_TYPES = {"bool", "char", "unsigned char", "short", "unsigned short", "int", "unsigned int",
                "long", "unsigned long", "float", "double", "string",
                "uint", "ulong", "uchar", "ushort"}


def step(label, fn):
    start = time.time()
    entry = {"step": label}
    try:
        entry["result"] = fn()
    except Exception:
        entry["error"] = traceback.format_exc(limit=2).strip().splitlines()[-1]
        report["ok"] = False
    entry["seconds"] = round(time.time() - start, 3)
    report["steps"].append(entry)
    return entry.get("result"), "error" not in entry


def finish(code=0):
    with open(result_path, "w", encoding="utf-8") as stream:
        json.dump(session, stream, indent=1, default=repr)
    # Exit normally: os._exit would skip flushing Maya's C-level stdout, which
    # is where its Warning/Error lines are written.
    sys.stdout.flush()
    sys.exit(code)


try:
    start = time.time()
    import maya.standalone
    maya.standalone.initialize(name="python")
    import maya.cmds as cmds
    cmds.loadPlugin("bifrostGraph")
    session["bifrost_version"] = cmds.pluginInfo("bifrostGraph", q=True, version=True)
    session["timing"]["startup"] = round(time.time() - start, 3)
except Exception:
    session["fatal"] = traceback.format_exc()
    finish(0)


def run_graph(index, spec):
    global report
    report = {"ok": True, "steps": [], "outputs": {}, "timing": {}}
    session["graphs"].append(report)
    # The wrapper collects Maya's Warning/Error lines between these markers,
    # so library-loading noise from startup stays out of the report.
    print(f"@@BIFROST_GRAPH_START {index}", flush=True)
    if spec.get("graph"):
        graph, ok = step(f"import graph {spec['graph']}",
                         lambda: cmds.bifrostGraph(importGraphAsShape=spec["graph"]))
        if not ok:
            print(f"@@BIFROST_GRAPH_END {index}", flush=True)
            return
        report["graph_nodes"] = cmds.vnnCompound(graph, "/", listNodes=True)
    else:
        graph = cmds.createNode("bifrostGraphShape")
    report["graph"] = graph
    for scene in spec.get("import", []):
        step(f"import {scene}", lambda: cmds.file(scene, i=True))

    names, types = {}, {}
    for node in spec.get("nodes", []):
        ntype = node["type"]
        namespace, _, short = ntype.rpartition("::")
        created, ok = step(f"add {ntype}", lambda: cmds.vnnCompound(
            graph, "/", addNode=f"BifrostGraph,{namespace},{short}"))
        if ok and created:
            actual = created[0]
            wanted = node.get("name")
            if wanted and wanted != actual:
                renamed, ok = step(f"rename {actual} -> {wanted}",
                                   lambda: cmds.vnnCompound(graph, "/", renameNode=(actual, wanted)))
                actual = wanted if ok else actual
            names[node.get("name", actual)] = actual
            types[node.get("name", actual)] = ntype
    report["node_names"] = names
    report["node_types"] = types

    for port, ptype in spec.get("inputs", {}).items():
        step(f"graph input {port}: {ptype}",
             lambda: cmds.vnnNode(graph, "/input", createOutputPort=(port, ptype)))
    existing = set(cmds.listAttr(graph, userDefined=True) or []) if spec.get("graph") else set()
    for port, ptype in spec.get("outputs", {}).items():
        if port in existing:
            continue
        step(f"graph output {port}: {ptype}",
             lambda: cmds.vnnNode(graph, "/output", createInputPort=(port, ptype)))

    def endpoint(text):
        # "node.port" -> "/node.port"; ".port" (graph boundary) stays as is.
        if text.startswith("."):
            return text
        node, _, port = text.partition(".")
        return f"/{names.get(node, node)}.{port}"

    for path, value in spec.get("values", {}).items():
        node, _, port = path.partition(".")
        step(f"set {path} = {value}", lambda: cmds.vnnNode(
            graph, f"/{names.get(node, node)}", setPortDefaultValues=(port, str(value))))
    def connect_fan_in(source, target):
        # "node.port[]": a new fan-in child named after the source port, as Autodesk's
        # bifrost_usd graph_api.connect_to_fanin_port does (vnnConnect can't target the
        # parent of a fan-in port directly).
        node, _, parent = target[:-2].partition(".")
        child = source.rpartition(".")[2]
        existing = cmds.vnnNode(graph, f"/{names.get(node, node)}", listPortChildren=parent) or []
        name, suffix = child, 1
        while name in existing:
            name, suffix = f"{child}{suffix}", suffix + 1
        cmds.vnnChangeBracket(graph, open=True)
        try:
            cmds.vnnNode(graph, f"/{names.get(node, node)}", createInputPort=(f"{parent}.{name}", "auto"))
            cmds.vnnConnect(graph, endpoint(source), f"/{names.get(node, node)}.{parent}.{name}")
        finally:
            cmds.vnnChangeBracket(graph, close=True)
        return f"{parent}.{name}"

    for source, target in spec.get("connections", []):
        if target.endswith("[]"):
            step(f"connect {source} -> {target}", lambda: connect_fan_in(source, target))
        else:
            step(f"connect {source} -> {target}", lambda: cmds.vnnConnect(graph, endpoint(source), endpoint(target)))

    for attr, value in spec.get("attributes", {}).items():
        step(f"setAttr {attr} = {value}", lambda: cmds.setAttr(f"{graph}.{attr}", value))

    evaluate_start = time.time()
    for port, ptype in spec.get("outputs", {}).items():
        if ptype in SCALAR_TYPES:
            value, _ = step(f"read {port}", lambda: cmds.getAttr(f"{graph}.{port}"))
            report["outputs"][port] = value
            continue
        before = set(cmds.ls(type="mesh") or [])
        step(f"geometry {port}", lambda: cmds.bifrostGraph(graph, createMayaGeometry=port))
        meshes = sorted(set(cmds.ls(type="mesh") or []) - before)
        info = {"type": ptype, "meshes": len(meshes), "vertices": 0, "faces": 0}
        for mesh in meshes:
            counts = cmds.polyEvaluate(mesh, vertex=True, face=True)
            if isinstance(counts, dict):
                info["vertices"] += counts.get("vertex", 0)
                info["faces"] += counts.get("face", 0)
        if meshes and info["vertices"]:
            info["bbox"] = [round(v, 4) for v in cmds.exactWorldBoundingBox(meshes)]
        if not meshes:
            info["note"] = "no Maya mesh produced (empty, points, volumes or instances); read a count instead"
        report["outputs"][port] = info
    report["timing"]["evaluate"] = round(time.time() - evaluate_start, 3)

    if spec.get("save_scene"):
        step(f"save {spec['save_scene']}", lambda: (cmds.file(rename=spec["save_scene"]),
                                                    cmds.file(save=True, type="mayaAscii"))[1])
    print(f"@@BIFROST_GRAPH_END {index}", flush=True)


for index, spec in enumerate(specs):
    try:
        run_graph(index, spec)
    except Exception:
        report["ok"] = False
        report["fatal"] = traceback.format_exc()
        print(f"@@BIFROST_GRAPH_END {index}", flush=True)
session["single"] = single
finish(0)
