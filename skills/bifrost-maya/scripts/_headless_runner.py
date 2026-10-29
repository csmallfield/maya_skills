"""Runs inside mayapy for bifrost_headless.py. Not meant to be called directly.

One-shot mode: `mayapy _headless_runner.py spec.json result.json` builds the
graphs, reads the requested outputs and writes a JSON report. The persistent
worker (`_headless_worker.py`) imports this module and calls `run_graph` for
each request instead.
"""
import json
import sys
import time
import traceback

SCALAR_TYPES = {"bool", "char", "unsigned char", "short", "unsigned short", "int", "unsigned int",
                "long", "unsigned long", "float", "double", "string",
                "uint", "ulong", "uchar", "ushort"}

cmds = None


def init_maya():
    """Start Maya standalone and load Bifrost. Returns session info."""
    global cmds
    start = time.time()
    import maya.standalone
    maya.standalone.initialize(name="python")
    import maya.cmds
    cmds = maya.cmds
    cmds.loadPlugin("bifrostGraph")
    return {"bifrost_version": cmds.pluginInfo("bifrostGraph", q=True, version=True),
            "startup": round(time.time() - start, 3)}


def make_step(report):
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
    return step


def mesh_stats(meshes):
    info = {"meshes": len(meshes), "vertices": 0, "faces": 0}
    for mesh in meshes:
        counts = cmds.polyEvaluate(mesh, vertex=True, face=True)
        if isinstance(counts, dict):
            info["vertices"] += counts.get("vertex", 0)
            info["faces"] += counts.get("face", 0)
    if meshes and info["vertices"]:
        info["bbox"] = [round(v, 4) for v in cmds.exactWorldBoundingBox(meshes)]
    return info


def run_graph(index, spec):
    """Build and evaluate one spec in the current scene. Returns its report."""
    report = {"ok": True, "steps": [], "outputs": {}, "timing": {}}
    step = make_step(report)
    # The wrapper collects Maya's output between these markers, so library
    # loading noise stays out of the report.
    print(f"@@BIFROST_GRAPH_START {index}", flush=True)
    try:
        build_and_read(spec, report, step)
    except Exception:
        report["ok"] = False
        report["fatal"] = traceback.format_exc()
    print(f"@@BIFROST_GRAPH_END {index}", flush=True)
    return report


def build_and_read(spec, report, step):
    if spec.get("graph"):
        graph, ok = step(f"import graph {spec['graph']}",
                         lambda: cmds.bifrostGraph(importGraphAsShape=spec["graph"]))
        if not ok:
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
                _, ok = step(f"rename {actual} -> {wanted}",
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
        current = cmds.vnnNode(graph, f"/{names.get(node, node)}", listPortChildren=parent) or []
        name, suffix = child, 1
        while name in current:
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

    outputs = dict(spec.get("outputs", {}))
    if spec.get("point_counts", True):
        # Points, volumes and instances produce no Maya mesh, so also count the points of every
        # Object output, fed from the same source (`<port>__points`). This is what shows a
        # particle sim growing over frames.
        for source, target in spec.get("connections", []):
            port = target[1:] if target.startswith(".") else None
            if port and outputs.get(port) == "Object":
                counter = f"{port}__count_points"
                made, ok = step(f"add point count for {port}", lambda: cmds.vnnCompound(
                    graph, "/", addNode="BifrostGraph,Geometry::Properties,get_point_count"))
                if not ok:
                    continue
                cmds.vnnCompound(graph, "/", renameNode=(made[0], counter))
                cmds.vnnNode(graph, "/output", createInputPort=(f"{port}__points", "uint"))
                cmds.vnnConnect(graph, endpoint(source), f"/{counter}.geometry")
                cmds.vnnConnect(graph, f"/{counter}.count", f".{port}__points")
                outputs[f"{port}__points"] = "uint"
    frames = spec.get("frames")
    evaluate_start = time.time()
    meshes = {}
    if frames:
        start, end = frames
        cmds.playbackOptions(minTime=start, maxTime=end)
        cmds.currentTime(start)
    for port, ptype in outputs.items():
        if ptype not in SCALAR_TYPES:
            before = set(cmds.ls(type="mesh") or [])
            step(f"geometry {port}", lambda: cmds.bifrostGraph(graph, createMayaGeometry=port))
            meshes[port] = sorted(set(cmds.ls(type="mesh") or []) - before)

    def read_all(record=True):
        values = {}
        for port, ptype in outputs.items():
            if ptype in SCALAR_TYPES:
                if record:
                    value, _ = step(f"read {port}", lambda: cmds.getAttr(f"{graph}.{port}"))
                else:
                    value = cmds.getAttr(f"{graph}.{port}")
                values[port] = value
            else:
                info = {"type": ptype, **mesh_stats(meshes.get(port, []))}
                if not info["meshes"]:
                    info["note"] = "no Maya mesh produced (empty, points, volumes or instances); read a count instead"
                values[port] = info
        return values

    if not frames:
        report["outputs"] = read_all()
    else:
        # Simulations need every frame evaluated in order; read outputs only at the sample frames.
        start, end = frames
        samples = sorted(set(spec.get("sample_frames") or [end]))
        report["frames"] = {}
        frame_times = []
        # Evaluate synchronously, and pull every output on every frame: a simulation only
        # advances when each frame is actually computed, in order.
        step("disable async evaluation", lambda: cmds.bifrostGraph(graph, enableAsync=False))
        for frame in range(int(start), int(end) + 1):
            tick = time.time()
            cmds.currentTime(frame, update=True)
            values = read_all(record=False)
            frame_times.append(time.time() - tick)
            if frame in samples:
                report["frames"][str(frame)] = values
        report["outputs"] = report["frames"].get(str(samples[-1]), {})
        report["timing"]["frames"] = len(frame_times)
        report["timing"]["slowest_frame"] = round(max(frame_times), 3) if frame_times else 0
    report["timing"]["evaluate"] = round(time.time() - evaluate_start, 3)

    if spec.get("save_scene"):
        step(f"save {spec['save_scene']}", lambda: (cmds.file(rename=spec["save_scene"]),
                                                    cmds.file(save=True, type="mayaAscii"))[1])


def main():
    spec_path, result_path = sys.argv[1], sys.argv[2]
    with open(spec_path, encoding="utf-8") as stream:
        specs = json.load(stream)
    single = isinstance(specs, dict)
    specs = [specs] if single else specs
    session = {"graphs": [], "timing": {}, "single": single}
    try:
        info = init_maya()
        session["bifrost_version"] = info["bifrost_version"]
        session["timing"]["startup"] = info["startup"]
        for index, spec in enumerate(specs):
            cmds.file(new=True, force=True)
            session["graphs"].append(run_graph(index, spec))
    except Exception:
        session["fatal"] = traceback.format_exc()
    with open(result_path, "w", encoding="utf-8") as stream:
        json.dump(session, stream, indent=1, default=repr)
    # Exit normally: os._exit would skip flushing Maya's C-level stdout, which
    # is where its Warning/Error lines are written.
    sys.stdout.flush()
    sys.exit(0)


if __name__ == "__main__":
    main()
