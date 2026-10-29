#!/usr/bin/env python3
"""Look up exact Bifrost nodes from the index built by build_node_index.py.

    node_info.py create_mesh_cube              # exact or short name -> ports, defaults, summary
    node_info.py --search "scatter on surface" # ranked search over names, ports and doc summaries
    node_info.py scatter_points --doc          # print the shipped Autodesk doc
    node_info.py Core::Math::add --overloads   # every exact signature, read from the install
    node_info.py --type Modeling::Points::ScatteringMode
    node_info.py --renamed Geometry::Tags::Internal::merge_tags

Use --version to pick an index under references/bifrost-<version> (default: newest).
Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def version_key(text: str):
    return tuple(int(part) for part in re.findall(r"\d+", text))


def index_dir(version: str | None) -> Path:
    folders = sorted(ROOT.glob("references/bifrost-*/node-index.json"), key=lambda p: version_key(p.parent.name))
    if not folders:
        sys.exit("No node index. Run scripts/build_node_index.py <bifrost install>/bifrost first.")
    if version:
        for path in folders:
            if path.parent.name == f"bifrost-{version}":
                return path.parent
        sys.exit(f"No index for {version}; have {[p.parent.name for p in folders]}")
    return folders[-1].parent


def load(folder: Path, name: str):
    with (folder / name).open(encoding="utf-8") as stream:
        return json.load(stream)


def bifrost_root(folder: Path) -> Path:
    return Path(os.environ.get("BIFROST_ROOT") or load(folder, "index-meta.json")["bifrost_root"])


def resolve(nodes: dict, query: str, include_internal: bool) -> list[str]:
    if query in nodes:
        return [query]
    lowered = query.lower()
    hits = [n for n in nodes if n.lower().rsplit("::", 1)[-1] == lowered.rsplit("::", 1)[-1]
            and n.lower().endswith(lowered)]
    if not include_internal:
        public = [n for n in hits if not nodes[n]["internal"]]
        hits = public or hits
    return sorted(hits)


def format_default(value) -> str:
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}: {format_default(v)}" for k, v in value.items()) + "}"
    return str(value)


def show(name: str, entry: dict) -> None:
    flags = [entry["kind"]]
    if entry["internal"]:
        flags.append("INTERNAL")
    if entry["kind"] == "builtin":
        flags.append(f"ports observed in {entry.get('observed_uses', 0)} shipped uses, not a full signature")
    if entry["overloads"] > 1:
        flags.append(f"{entry['overloads']} overloads")
    print(f"{name}  [{', '.join(flags)}]")
    if entry["summary"]:
        print(f"  {entry['summary']}")
    for direction in ("input", "output"):
        ports = [p for p in entry["ports"] if p["dir"] == direction]
        if not ports:
            continue
        print(f"  {direction}s:")
        for port in ports:
            types = " | ".join(port["types"]) + (f" | (+{port['more_types']} more)" if port.get("more_types") else "")
            default = f" = {format_default(port['default'])}" if "default" in port else ""
            print(f"    {port['name']}: {types}{default}")
    if entry["dependencies"]:
        print("  dependencies: " + ", ".join(f"{k} {v}" for k, v in entry["dependencies"].items()))
    print(f"  library: {entry['library']}" + (f"   doc: {entry['doc']}" if entry["doc"] else ""))


def search(nodes: dict, query: str, limit: int, include_internal: bool) -> None:
    terms = [t for t in re.split(r"[^a-z0-9_]+", query.lower()) if t]
    scored = []
    for name, entry in nodes.items():
        if entry["internal"] and not include_internal:
            continue
        short = name.rsplit("::", 1)[-1].lower()
        path = name.lower()
        ports = " ".join(p["name"].lower() for p in entry["ports"])
        summary = entry["summary"].lower()
        score = 0.0
        for term in terms:
            if term == short:
                score += 12
            elif term in short:
                score += 6
            elif term in path:
                score += 3
            if re.search(rf"\b{re.escape(term)}", summary):
                score += 2
            if term in ports:
                score += 1
        if score:
            scored.append((score, -len(name), name))
    for score, _, name in sorted(scored, reverse=True)[:limit]:
        summary = nodes[name]["summary"]
        print(f"{score:5.1f}  {name}")
        if summary:
            print(f"       {summary[:160]}")


def overloads(folder: Path, name: str, entry: dict) -> None:
    if entry["kind"] == "builtin":
        print("  (built-in: no library signature; types resolve from connections)")
        return
    path = bifrost_root(folder) / entry["library"]
    if not path.is_file():
        sys.exit(f"Library not found at {path}; set BIFROST_ROOT to the install's bifrost folder.")
    with path.open(encoding="utf-8-sig") as stream:
        document = json.load(stream)
    for record in document.get(entry["kind"] + "s", []):
        if record["name"] != name:
            continue
        ins = ", ".join(f"{p['portName']}: {p.get('portType', 'auto')}" for p in record.get("ports", [])
                        if p["portDirection"] == "input")
        outs = ", ".join(f"{p['portName']}: {p.get('portType', 'auto')}" for p in record.get("ports", [])
                         if p["portDirection"] == "output")
        print(f"({ins}) -> ({outs})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Exact Bifrost node lookup.")
    parser.add_argument("name", nargs="?", help="fully qualified or short node name")
    parser.add_argument("--search", help="ranked search query")
    parser.add_argument("--doc", action="store_true", help="print the shipped documentation")
    parser.add_argument("--overloads", action="store_true", help="list every exact signature")
    parser.add_argument("--type", help="show an enum or struct type")
    parser.add_argument("--renamed", help="check whether an old node name was renamed")
    parser.add_argument("--internal", action="store_true", help="include internal nodes")
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--version", help="index version, e.g. 3.0.0.0")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    folder = index_dir(args.version)
    print(f"# Bifrost {folder.name.removeprefix('bifrost-')} (installed library)")
    if args.type:
        types = load(folder, "types.json")
        matches = [t for t in types if t == args.type or t.lower().endswith(args.type.lower())]
        for name in matches:
            print(name, json.dumps(types[name], indent=1))
        return 0 if matches else 1
    if args.renamed:
        renames = load(folder, "renames.json")
        hit = renames.get(args.renamed)
        print(json.dumps(hit, indent=1) if hit else f"{args.renamed}: no rename recorded")
        return 0
    nodes = load(folder, "node-index.json")
    if args.search:
        search(nodes, args.search, args.limit, args.internal)
        return 0
    if not args.name:
        parser.error("give a node name, --search, --type or --renamed")
    hits = resolve(nodes, args.name, args.internal)
    if not hits:
        renamed = load(folder, "renames.json").get(args.name)
        if renamed:
            print(f"{args.name} was renamed to {renamed['new']} (changeset {renamed['library']} {renamed['version']})")
            hits = resolve(nodes, renamed["new"], True)
        if not hits:
            print(f"No node named {args.name!r}. Try --search.")
            return 1
    for name in hits:
        entry = nodes[name]
        show(name, entry)
        if args.overloads:
            overloads(folder, name, entry)
        if args.doc:
            if not entry["doc"]:
                print("  (no shipped doc)")
            else:
                doc = bifrost_root(folder) / entry["doc"]
                print(doc.read_text(encoding="utf-8", errors="replace") if doc.is_file() else f"  doc missing: {doc}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
