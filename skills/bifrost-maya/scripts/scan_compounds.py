#!/usr/bin/env python3
"""Compile-check every installed compound in a folder against the current Bifrost.

    scan_compounds.py [FOLDER] [--recursive] [--out REPORT.md] [--json REPORT.json]

FOLDER defaults to the user's compounds folder (~/Autodesk/Bifrost/Compounds).
Each top-level compound in each JSON file is compiled by name with bifcmd from
the installed libraries (about 10 s each), so the files are never copied or
changed. Compounds using USD types are listed as needing the USD pack, which
bifcmd runs without here, and compounds with untyped (auto) inputs are listed
separately because bifcmd can't compile them outside a graph. Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bifcmd_check  # noqa: E402


def compounds_in(path: Path) -> list[str]:
    try:
        document = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return []
    if not isinstance(document, dict):
        return []
    return [c["name"] for c in document.get("compounds", []) if isinstance(c, dict) and c.get("name")]


def scan(folder: Path, recursive: bool) -> list[dict]:
    files = sorted(folder.rglob("*.json") if recursive else folder.glob("*.json"))
    rows = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        for name in compounds_in(path):
            row = {"file": str(path.relative_to(folder)), "compound": name}
            if "BifrostUsd::" in text:
                row["status"] = "needs USD pack"
                rows.append(row)
                continue
            start = time.time()
            result, code = bifcmd_check.check(None, name, False, [], None, False, 300)
            row["seconds"] = round(time.time() - start, 1)
            row["status"] = {0: "compiles", 1: "fails", 2: "crash"}[code]
            failed = [stage for stage, ok in (result.get("stages") or {}).items() if not ok]
            if failed:
                row["failed_stage"] = failed[0]
            row["errors"] = [e.splitlines()[-1].strip() for e in result.get("errors", [])][:3]
            all_errors = " ".join(result.get("errors", []))
            if code == 1 and "explicitly set the type of this compound input port" in all_errors:
                # bifcmd can't compile a compound with untyped (auto) inputs on its own;
                # in Maya the connected inputs give them a type. Not a 3.0 failure.
                row["status"] = "auto inputs (needs a graph)"
            if result.get("fatal"):
                row["errors"].append(result["fatal"])
            print(f"{row['status']:15} {name}", flush=True)
            rows.append(row)
    return rows


def markdown(rows: list[dict], folder: Path, version: str) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = [f"# Compound compatibility: {folder}", "",
             f"Bifrost {version}, compiled by name with bifcmd ({time.strftime('%Y-%m-%d')}). "
             + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())) + ".", "",
             "| Compound | File | Status | Detail |", "|---|---|---|---|"]
    for row in rows:
        detail = "; ".join(row.get("errors", [])) or row.get("failed_stage", "")
        lines.append(f"| `{row['compound']}` | {row['file']} | {row['status']} | {detail.replace('|', '/')} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile-check installed compounds with bifcmd.")
    parser.add_argument("folder", nargs="?", type=Path, default=Path.home() / "Autodesk" / "Bifrost" / "Compounds")
    parser.add_argument("--recursive", action="store_true", help="include library subfolders (slow)")
    parser.add_argument("--out", type=Path, help="write a Markdown report")
    parser.add_argument("--json", type=Path, help="write a JSON report")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    rows = scan(args.folder, args.recursive)
    version = bifcmd_check.bifrost_root().parent.name
    if args.out:
        args.out.write_text(markdown(rows, args.folder, version), encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0 if all(row["status"] != "fails" and row["status"] != "crash" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
