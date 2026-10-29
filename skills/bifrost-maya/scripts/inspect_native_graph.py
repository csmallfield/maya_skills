#!/usr/bin/env python3
"""Inspect a native file at one compound scope; do not flatten the entire graph."""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def walk(compound: dict, path: str):
    yield path, compound
    for child in compound.get("compounds", []):
        yield from walk(child, path + "/" + child["name"])


def main() -> int:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--path", default="root")
    parser.add_argument("--tree", action="store_true")
    parser.add_argument("--connections", type=int, default=15)
    parser.add_argument("--values", type=int, default=10)
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8-sig"))
        roots = data["compounds"]
        scopes = dict(pair for i, root in enumerate(roots) for pair in walk(root, "root" if len(roots) == 1 else f"root[{i}]"))
        if args.tree:
            for path, c in scopes.items():
                print(f"{path}: {len(c.get('compoundNodes', []))} nodes" + (" [for_each]" if "forEachCompound" in c else ""))
            return 0
        c = scopes[args.path]
        summary = {"path": args.path, "name": c["name"], "ports": c.get("ports", []),
                   "local_definitions": [x["name"] for x in c.get("compounds", [])],
                   "nodes": [{k: v for k, v in n.items() if k != "metadata"} for n in c.get("compoundNodes", [])],
                   "node_type_counts": dict(Counter(n.get("nodeType", "VALUE:" + n.get("valueType", "?")) for n in c.get("compoundNodes", []))),
                   "connections_total": len(c.get("connections", [])),
                   "connections": c.get("connections", [])[:max(0, args.connections)],
                   "values_total": len(c.get("values", [])),
                   "values": c.get("values", [])[:max(0, args.values)],
                   "libraryDependencies": c.get("libraryDependencies", {})}
        if "forEachCompound" in c:
            summary["forEachCompound"] = c["forEachCompound"]
        print(json.dumps(summary, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Cannot inspect native graph/path: {exc}. Use --tree for available paths.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
