#!/usr/bin/env python3
"""Conservative native-Bifrost preflight. This is NOT an Amino compiler.

Scope: the authored native-export pattern in assets/native-examples. External
interfaces are partial source evidence; overloads and runtime types are not
inferred. Unknown evidence fails only with --strict-evidence. Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def load_evidence() -> dict[str, Any]:
    """Combine observed native endpoints with exact custom public port names.

    Unioning port names across overloads is an existence check ONLY. It does not
    establish that one compatible overload contains all the used ports/types.
    """
    evidence: dict[str, Any] = {}
    for rel in ("workflow-data/node-usage-index.json", "compound-data/node-usage-index.json"):
        for name in read_json(ROOT / "references" / rel):
            if "::" in name and not name.startswith("Value::"):
                evidence.setdefault(name, {"inputs": set(), "outputs": set()})
    observed = read_json(ROOT / "references/native-endpoint-evidence.json")
    for name, record in observed["nodes"].items():
        entry = evidence.setdefault(name, {"inputs": set(), "outputs": set()})
        for key in ("inputs", "outputs", "fan_in_roots", "multi_input_roots"):
            entry.setdefault(key, set()).update(record.get(key, []))
    interfaces = read_json(ROOT / "references/compound-data/interface-index.json")
    for name, overloads in interfaces.items():
        entry = evidence.setdefault(name, {"inputs": set(), "outputs": set()})
        for overload in overloads:
            for port in overload.get("ports", []):
                key = {"input": "inputs", "output": "outputs"}.get(port.get("direction"))
                if key:
                    entry[key].add(port["name"])
    return evidence


def validate_document(document: Any, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return structural errors, evidence gaps and counts, without running Maya."""
    if evidence is None:
        evidence = load_evidence()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    calls: list[dict[str, str]] = []
    external: set[str] = set()
    stats = {"definition_scopes": 0, "stored_nodes": 0, "connections": 0,
             "loop_definitions": 0}
    seen_warnings: set[tuple[str, str, str]] = set()

    def issue(code: str, path: str, detail: str, *, warning: bool = False) -> None:
        record = {"code": code, "path": path, "detail": detail}
        if warning:
            marker = (code, path, detail)
            if marker not in seen_warnings:
                warnings.append(record)
                seen_warnings.add(marker)
        else:
            errors.append(record)

    def result() -> dict[str, Any]:
        return {"structural_ok": not errors, "evidence_complete_for_used_spellings": not warnings,
                "errors": errors, "evidence_warnings": warnings,
                "stats": {**stats, "local_calls": len(calls), "external_type_count": len(external)},
                "local_references": calls, "external_types": sorted(external),
                "limits": ["Not Maya/Bifrost compilation or execution.",
                           "No overload/type inference, PPG evaluation, render or timing validation.",
                           "Immediate-scope rules are a conservative authoring profile.",
                           "Observed endpoint evidence is partial and version-specific."]}

    if not isinstance(document, dict) or not isinstance(document.get("header"), dict) or not isinstance(document.get("compounds"), list) or not document["compounds"]:
        issue("NOT_NATIVE_COMPOUND", "$", "Expected a native header and nonempty compounds array, not a graph blueprint.")
        return result()
    metadata = document["header"].get("metadata")
    if not isinstance(metadata, list) or not any(isinstance(m, dict) and m.get("metaName") == "adskFileFormatVersion" for m in metadata):
        issue("MISSING_FORMAT_VERSION", "$/header", "Missing adskFileFormatVersion metadata.")
    else:
        version = next(m.get("metaValue") for m in metadata if isinstance(m, dict) and m.get("metaName") == "adskFileFormatVersion")
        if version != "100L":
            issue("UNOBSERVED_FORMAT_VERSION", "$/header", repr(version), warning=True)
    for key in ("namespaces", "types"):
        if not isinstance(document.get(key), list):
            issue("BAD_ENVELOPE_LIST", "$", key + " must be an array in this export profile.")
    roots = {c.get("name"): c for c in document["compounds"] if isinstance(c, dict) and isinstance(c.get("name"), str) and "::" in c["name"]}

    def visit(compound: Any, path: str) -> None:
        if not isinstance(compound, dict):
            issue("BAD_DEFINITION", path, "Expected a compound object.")
            return
        stats["definition_scopes"] += 1
        if not isinstance(compound.get("name"), str) or not compound["name"]:
            issue("MISSING_COMPOUND_NAME", path, "Compound name must be a nonempty string.")
        groups: dict[str, list[dict[str, Any]]] = {}
        for key in ("ports", "compoundNodes", "connections", "values", "compounds"):
            value = compound.get(key, [])
            if not isinstance(value, list) or any(not isinstance(x, dict) for x in value):
                issue("BAD_DEFINITION_LIST", path, key + " must contain objects.")
                value = []
            groups[key] = value
        ports: dict[str, dict[str, Any]] = {}
        for p in groups["ports"]:
            name = p.get("portName")
            if not isinstance(name, str) or not name:
                issue("BAD_PORT_NAME", path, repr(name))
                continue
            if name in ports:
                issue("DUPLICATE_PORT", path, name)
            ports[name] = p
            if p.get("portDirection") not in ("input", "output"):
                issue("UNSUPPORTED_PORT_DIRECTION", path, name, warning=True)
        local: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in groups["compounds"]:
            if isinstance(c.get("name"), str):
                local[c["name"]].append(c)
        for name, overloads in local.items():
            if len(overloads) > 1:
                issue("LOCAL_OVERLOAD_REQUIRES_REVIEW", path, name, warning=True)
        nodes: dict[str, dict[str, Any]] = {}
        resolved: dict[str, list[dict[str, Any]]] = {}
        for n in groups["compoundNodes"]:
            name = n.get("nodeName")
            if not isinstance(name, str) or not name:
                issue("BAD_NODE_NAME", path, repr(name))
                continue
            if name in nodes:
                issue("DUPLICATE_NODE", path, name)
            nodes[name] = n
            kind = n.get("nodeType")
            if kind in local:
                resolved[name] = local[kind]
                calls.append({"path": path, "node": name, "type": kind, "resolution": "immediate_scope"})
            elif isinstance(kind, str) and "::" in kind:
                if kind in roots:
                    resolved[name] = [roots[kind]]
                else:
                    external.add(kind)
                    if kind not in evidence:
                        issue("UNKNOWN_EXTERNAL_TYPE", path, kind, warning=True)
            elif kind:
                issue("UNRESOLVED_LOCAL_TYPE", path, f"{name} -> {kind}; no definition in the calling scope.")
            elif not n.get("valueType"):
                issue("MISSING_NODE_TYPE", path, name)
            fan = n.get("fanInPortNames", {})
            if not isinstance(fan, dict) or any(not isinstance(v, list) or any(not isinstance(x, str) for x in v) for v in fan.values()):
                issue("BAD_FAN_IN_DECLARATION", path, name)
            multi = n.get("multiInPortNames", [])
            if not isinstance(multi, list) or any(not isinstance(x, str) for x in multi):
                issue("BAD_MULTI_INPUT_DECLARATION", path, name)
        stats["stored_nodes"] += len(groups["compoundNodes"])
        stats["connections"] += len(groups["connections"])
        if "forEachCompound" in compound:
            stats["loop_definitions"] += 1
            marker = compound["forEachCompound"]
            if not isinstance(marker, dict) or not isinstance(marker.get("ports"), list):
                issue("BAD_FOR_EACH_MARKER", path, "Expected native forEachCompound.ports array.")
            for p in ports.values():
                if p.get("portIterationTarget") in (True, "true") and not str(p.get("portType", "")).startswith("array<"):
                    issue("NON_ARRAY_ITERATION_TARGET", path, p["portName"])

        def endpoint(ep: Any, direction: str) -> str | None:
            if not isinstance(ep, str) or "." not in ep:
                issue("BAD_ENDPOINT", path, repr(ep))
                return None
            node_name, suffix = ep.split(".", 1)
            parts = suffix.split(".")
            port = parts[0]
            if not port:
                issue("BAD_ENDPOINT", path, ep)
                return None
            if not node_name:
                expected = "input" if direction == "output" else "output"
                if port not in ports:
                    issue("UNKNOWN_INTERFACE_PORT", path, ep)
                elif ports[port].get("portDirection") != expected:
                    issue("INTERFACE_DIRECTION", path, ep + " should be " + expected)
                return None
            if node_name not in nodes:
                issue("UNKNOWN_ENDPOINT_NODE", path, ep)
                return None
            node = nodes[node_name]
            if node_name in resolved:
                matches = [p for c in resolved[node_name] for p in c.get("ports", []) if p.get("portName") == port]
                if not matches:
                    issue("UNKNOWN_LOCAL_PORT", path, ep)
                elif not any(p.get("portDirection") == direction for p in matches):
                    issue("LOCAL_PORT_DIRECTION", path, ep + " should be " + direction)
            elif not node.get("nodeType") and node.get("valueType"):
                expected = "output" if direction == "output" else "value"
                if port != expected:
                    issue("VALUE_NODE_PORT", path, ep + "; expected " + expected)
            else:
                kind = node.get("nodeType", "")
                entry = evidence.get(kind)
                key = "outputs" if direction == "output" else "inputs"
                if entry is not None and port not in entry.get(key, set()):
                    issue("UNOBSERVED_EXTERNAL_PORT", path, f"{kind}.{port} ({direction})", warning=True)
            if direction == "input" and len(parts) > 1:
                fan = node.get("fanInPortNames", {})
                observed = evidence.get(node.get("nodeType", ""), {})
                if port in observed.get("fan_in_roots", set()) or (isinstance(fan, dict) and port in fan):
                    if not isinstance(fan, dict) or not isinstance(fan.get(port), list) or parts[1] not in fan[port]:
                        issue("UNDECLARED_FAN_IN_CHILD", path, ep)
                multi = node.get("multiInPortNames", [])
                if port in observed.get("multi_input_roots", set()) or (port == "first" and "multiInPortNames" in node):
                    if not isinstance(multi, list) or parts[1] not in multi:
                        issue("UNDECLARED_MULTI_INPUT_CHILD", path, ep)
            return node_name

        targets: set[str] = set()
        driven: set[str] = set()
        adjacency: dict[str, set[str]] = {n: set() for n in nodes}
        for edge in groups["connections"]:
            source, target = edge.get("source"), edge.get("target")
            sn = endpoint(source, "output")
            tn = endpoint(target, "input")
            if isinstance(target, str):
                if target in targets:
                    issue("DUPLICATE_TARGET", path, target)
                targets.add(target)
                if target.startswith("."):
                    driven.add(target[1:].split(".", 1)[0])
            if sn in nodes and tn in nodes:
                adjacency[sn].add(tn)
        for name, port in ports.items():
            if port.get("portDirection") == "output" and name not in driven:
                issue("UNDRIVEN_OUTPUT", path, name)
        values: set[str] = set()
        for value in groups["values"]:
            name = value.get("valueName")
            if not isinstance(name, str):
                issue("BAD_VALUE_NAME", path, repr(name))
                continue
            if name in values:
                issue("DUPLICATE_VALUE", path, name)
            values.add(name)
            if "value" not in value or not value.get("valueType"):
                issue("UNTYPED_VALUE", path, name)
            endpoint(name, "input")
        degree = Counter({n: 0 for n in nodes})
        for followers in adjacency.values():
            for follower in followers:
                degree[follower] += 1
        queue = deque(n for n in nodes if degree[n] == 0)
        visited = 0
        while queue:
            n = queue.popleft()
            visited += 1
            for follower in adjacency[n]:
                degree[follower] -= 1
                if degree[follower] == 0:
                    queue.append(follower)
        if visited != len(nodes):
            issue("LOCAL_DATAFLOW_CYCLE", path, "Review explicit node-to-node cycle; loop/state semantics are not compiled here.")
        for i, child in enumerate(groups["compounds"]):
            visit(child, path + "/" + str(child.get("name", i)))

    for i, c in enumerate(document["compounds"]):
        visit(c, "root" if len(document["compounds"]) == 1 else f"root[{i}]")
    return result()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--strict-evidence", action="store_true", help="Fail on evidence gaps as well as structural errors.")
    parser.add_argument("--json-report", type=Path)
    args = parser.parse_args()
    try:
        report = validate_document(read_json(args.file))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Cannot inspect input/evidence: {exc}", file=sys.stderr)
        return 2
    failed = bool(report["errors"] or (args.strict_evidence and report["evidence_warnings"]))
    report["strict_evidence"] = args.strict_evidence
    report["passed_requested_checks"] = not failed
    report["source_file"] = args.file.name
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{'FAIL' if failed else 'PASS'}: {len(report['errors'])} structural errors, {len(report['evidence_warnings'])} evidence gaps; {report['stats']}")
    for item in report["errors"] + report["evidence_warnings"]:
        print(f"{item['code']} {item['path']}: {item['detail']}")
    print("Offline preflight only; not Maya compilation or a performance benchmark.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
