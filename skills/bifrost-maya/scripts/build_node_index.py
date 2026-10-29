#!/usr/bin/env python3
"""Build an exact node index from an installed Bifrost's shipped library JSON.

Reads every resources/*/jsonLibs/*.json (plus the newest USD pack), the
changesets and the shipped ENU docs, and writes compact indexes that
node_info.py queries. Source of truth is the install, not summaries.

    python scripts/build_node_index.py "C:/Program Files/Autodesk/Bifrost/Maya2026/3.0.0.0/bifrost"

Python stdlib only.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_TYPES_PER_PORT = 12


def read_json(path: str):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def version_key(text: str):
    return tuple(int(part) for part in re.findall(r"\d+", text))


def library_files(bifrost_root: Path) -> list[Path]:
    files = sorted(bifrost_root.glob("resources/*/jsonLibs/*.json"))
    packs = sorted(bifrost_root.glob("packs/*/*/resources/jsonLibs/*.json"))
    newest: dict[str, Path] = {}
    for path in packs:
        pack, version = path.parts[-5], path.parts[-4]
        if pack not in newest or version_key(version) > version_key(newest[pack].parts[-4]):
            newest[pack] = path
    return files + sorted(newest.values())


def meta_value(record: dict, name: str):
    for meta in record.get("metadata", []) or []:
        if meta.get("metaName") == name:
            return meta.get("metaValue")
    return None


def doc_summary(doc_path: Path | None) -> str:
    """First prose paragraph of a shipped doc, trimmed."""
    if not doc_path or not doc_path.is_file():
        return ""
    lines = doc_path.read_text(encoding="utf-8", errors="replace").splitlines()
    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("!["):
            if paragraph:
                break
            continue
        if not stripped:
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    text = " ".join(paragraph)
    return text if len(text) <= 400 else text[:397].rstrip() + "..."


def resolve_doc(json_path: Path, raw: str | None) -> Path | None:
    if not raw:
        return None
    return (json_path.parent / raw.replace("${language}", "ENU")).resolve()


def walk_compounds(record: dict):
    yield record
    for child in record.get("compounds", []) or []:
        yield from walk_compounds(child)


def add_builtins(bifrost_root: Path, nodes: dict, renamed: set[str]) -> None:
    """Record node types that are used but never defined in the libraries.

    These are Amino built-ins such as Core::Logic::if or the loop nodes. Their
    ports are only what shipped compounds and example graphs connect or set, so
    they are observed spellings, not full signatures.
    """
    observed: dict[str, dict] = {}
    files = library_files(bifrost_root) + sorted(bifrost_root.glob("resources/graphs/*/*.json"))
    for path in files:
        document = read_json(str(path))
        for top in document.get("compounds", []):
            for scope in walk_compounds(top):
                local = {c["name"] for c in scope.get("compounds", []) or []}
                types = {}
                for node in scope.get("compoundNodes", []) or []:
                    ntype = node.get("nodeType")
                    if ntype and ntype not in nodes and ntype not in local and ntype not in renamed and "::" in ntype:
                        types[node["nodeName"]] = ntype
                        observed.setdefault(ntype, {"inputs": set(), "outputs": set(), "uses": 0})["uses"] += 1
                for conn in scope.get("connections", []) or []:
                    for end, key in ((conn.get("source", ""), "outputs"), (conn.get("target", ""), "inputs")):
                        node, _, port = end.partition(".")
                        if node in types and port:
                            observed[types[node]][key].add(port.split(".")[0])
                for value in scope.get("values", []) or []:
                    node, _, port = value.get("valueName", "").partition(".")
                    if node in types and port:
                        observed[types[node]]["inputs"].add(port.split(".")[0])
    for name, record in observed.items():
        doc_path = None
        guess = name.replace("::", "_") + ".md"
        for candidate in bifrost_root.glob(f"resources/*/docs/ENU/{guess}"):
            doc_path = candidate
            break
        nodes[name] = {
            "kind": "builtin",
            "library": None,
            "overloads": 0,
            "doc": doc_path.relative_to(bifrost_root).as_posix() if doc_path else None,
            "summary": doc_summary(doc_path),
            "dependencies": {},
            "observed_uses": record["uses"],
            "ports": [{"name": p, "dir": "input", "types": ["observed"]} for p in sorted(record["inputs"])]
            + [{"name": p, "dir": "output", "types": ["observed"]} for p in sorted(record["outputs"])],
        }


def build(bifrost_root: Path, out_dir: Path) -> dict:
    nodes: dict[str, dict] = {}
    port_types: dict[str, dict[str, dict]] = defaultdict(dict)
    types: dict[str, dict] = {}
    internal_namespaces: set[str] = set()
    sources = []

    for path in library_files(bifrost_root):
        document = read_json(str(path))
        rel = path.relative_to(bifrost_root).as_posix()
        sources.append({"file": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        for namespace in document.get("namespaces", []):
            if meta_value(namespace, "internal") == "true":
                internal_namespaces.add(namespace["name"])
        for record in document.get("types", []):
            name = record.get("enumName") or record.get("structName") or record.get("name")
            if not name:
                continue
            if "enumMembers" in record:
                types[name] = {"kind": "enum", "library": rel,
                               "members": [m["enumKey"] for m in record["enumMembers"]]}
            elif "structMembers" in record:
                types[name] = {"kind": "struct", "library": rel,
                               "members": [{"name": m.get("structMemberName"), "type": m.get("structMemberType")}
                                           for m in record["structMembers"]]}
            else:
                types[name] = {"kind": "other", "library": rel}
        for kind in ("operators", "compounds"):
            for record in document.get(kind, []):
                name = record["name"]
                entry = nodes.get(name)
                if entry is None:
                    doc_path = resolve_doc(path, meta_value(record, "documentation"))
                    entry = nodes[name] = {
                        "kind": kind[:-1],
                        "library": rel,
                        "overloads": 0,
                        "doc": doc_path.relative_to(bifrost_root).as_posix()
                        if doc_path and doc_path.is_file() and doc_path.is_relative_to(bifrost_root) else None,
                        "summary": doc_summary(doc_path),
                        "dependencies": record.get("libraryDependencies", {}),
                        "ports": [],
                    }
                entry["overloads"] += 1
                seen = port_types[name]
                for port in record.get("ports", []):
                    pname = port["portName"]
                    slot = seen.get(pname)
                    if slot is None:
                        slot = seen[pname] = {"name": pname, "dir": port["portDirection"], "types": []}
                        entry["ports"].append(slot)
                        if "portDefault" in port:
                            slot["default"] = port["portDefault"]
                    ptype = port.get("portType") or "auto"
                    if ptype not in slot["types"]:
                        slot["types"].append(ptype)

    renames: dict[str, dict] = {}
    for path in sorted(bifrost_root.glob("resources/*/changesets/*.json")):
        for changeset in read_json(str(path)).get("changesets", []):
            for old, new in (changeset.get("nodeDefinitions") or {}).items():
                renames[old] = {"new": new, "library": changeset.get("library"),
                                "version": changeset.get("version")}

    add_builtins(bifrost_root, nodes, set(renames))

    for name, entry in nodes.items():
        namespace = name.rsplit("::", 1)[0]
        entry["internal"] = "::Internal" in name or namespace in internal_namespaces
        for slot in entry["ports"]:
            if len(slot["types"]) > MAX_TYPES_PER_PORT:
                slot["more_types"] = len(slot["types"]) - MAX_TYPES_PER_PORT
                slot["types"] = slot["types"][:MAX_TYPES_PER_PORT]

    version = bifrost_root.parent.name
    out_dir.mkdir(parents=True, exist_ok=True)
    write = lambda name, data: (out_dir / name).write_text(
        json.dumps(data, indent=0, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    write("node-index.json", dict(sorted(nodes.items())))
    write("types.json", dict(sorted(types.items())))
    write("renames.json", dict(sorted(renames.items())))
    meta = {
        "bifrost_version": version,
        "bifrost_root": bifrost_root.as_posix(),
        "nodes": len(nodes),
        "public_nodes": sum(1 for e in nodes.values() if not e["internal"]),
        "operator_overloads": sum(e["overloads"] for e in nodes.values() if e["kind"] == "operator"),
        "compounds": sum(1 for e in nodes.values() if e["kind"] == "compound"),
        "builtins": sum(1 for e in nodes.values() if e["kind"] == "builtin"),
        "types": len(types),
        "renames": len(renames),
        "sources": sources,
    }
    write("index-meta.json", meta)
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bifrost_root", help="install folder containing resources/ (…/<version>/bifrost)")
    parser.add_argument("--out", help="output folder (default references/bifrost-<version>)")
    args = parser.parse_args()
    bifrost_root = Path(args.bifrost_root).resolve()
    if not (bifrost_root / "resources").is_dir():
        parser.error(f"{bifrost_root} has no resources/ folder")
    out = Path(args.out) if args.out else ROOT / "references" / f"bifrost-{bifrost_root.parent.name}"
    meta = build(bifrost_root, out)
    print(json.dumps({k: v for k, v in meta.items() if k != "sources"}, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
