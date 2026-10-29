#!/usr/bin/env python3
"""Verify a native compound JSON file in three stages before delivering it.

    verify_compound.py FILE.json [--compound NS::name] [--set PORT=VALUE ...] [--fast] [--json]

1. static   - validate_native_graph.py with --strict-evidence (format, scope,
              exact 3.0 ports on shipped nodes). Instant.
2. compile  - bifcmd loads and compiles the file directly. About 10 s.
3. evaluate - a headless mayapy loads the file from a scratch library,
              unpacks the compound as a graph and reads its outputs: scalar
              values, or mesh/vertex/face counts for Object outputs. About 40 s.

`--frames START END` simulates that range for stage 3 (every frame computed in
order) and reports outputs at the start, middle and end frames. `--fast` skips stage 3. `--set` sets compound input values for stage 3
(Bifrost literals such as `floors=12`). Array<Object> outputs are merged and
counted. Later stages still run after an
earlier failure so one report shows everything, except that stage 3 is
skipped when compile fails.

Verdicts: VERIFIED (all stages ran and passed), PARTIAL (passed but a stage
was skipped), FAILED. Exit code 0 only for VERIFIED (or PARTIAL with --fast).
None of this is a render, a performance benchmark or an artistic check.
Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bifcmd_check  # noqa: E402
import bifrost_headless  # noqa: E402
import validate_native_graph  # noqa: E402

SCALARS = {"bool", "char", "unsigned char", "short", "unsigned short", "int",
           "unsigned int", "long", "unsigned long", "float", "double", "string",
           "uint", "ulong", "uchar", "ushort"}


def public_compound(document: dict, wanted: str | None) -> dict:
    tops = [c for c in document.get("compounds", []) if isinstance(c, dict)]
    if wanted:
        for compound in tops:
            if compound.get("name") == wanted:
                return compound
        sys.exit(f"{wanted} is not a top-level compound in the file; have {[c.get('name') for c in tops]}")
    if len(tops) != 1:
        sys.exit(f"File defines {len(tops)} top-level compounds; pick one with --compound: {[c.get('name') for c in tops]}")
    return tops[0]


def installed_names() -> dict[str, str]:
    """Top-level compound names in the user's compounds folder, mapped to their file."""
    folder = Path.home() / "Autodesk" / "Bifrost" / "Compounds"
    names: dict[str, str] = {}
    for path in folder.rglob("*.json") if folder.is_dir() else []:
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            continue
        for compound in document.get("compounds", []) if isinstance(document, dict) else []:
            if isinstance(compound, dict) and compound.get("name"):
                names[compound["name"]] = str(path)
    return names


def renamed_copy(document: dict, name: str, folder: Path) -> tuple[Path, str]:
    """Write a copy whose public compound has a unique name.

    Loading a file that redefines an installed compound crashes bifcmd, and the
    installed copy would shadow the file in a headless Maya.
    """
    new_name = f"{name}__verify"
    copy = json.loads(json.dumps(document))
    for compound in copy["compounds"]:
        if compound.get("name") == name:
            compound["name"] = new_name
    path = folder / "verify_copy.json"
    path.write_text(json.dumps(copy), encoding="utf-8")
    return path, new_name


def evaluation_spec(name: str, outputs: dict[str, str], sets: list[str],
                    frames: list[int] | None = None) -> tuple[dict, set[str]]:
    """Headless spec that places the compound as a node and wires every readable output.

    Scalars and Object outputs are wired straight to graph outputs. An
    array<Object> output gets a `merge_geometry` (read as one mesh) and an
    `array_size` (element count), so arrays of meshes are checked too.
    """
    spec = {"nodes": [{"type": name, "name": "c"}], "outputs": {}, "connections": [],
            "values": {f"c.{k}": v for k, v in (item.split("=", 1) for item in sets)}}
    readable = set()
    for port, ptype in outputs.items():
        if ptype in SCALARS or ptype == "Object":
            spec["outputs"][port] = ptype
            spec["connections"].append([f"c.{port}", f".{port}"])
        elif ptype == "array<Object>":
            spec["nodes"] += [{"type": "Modeling::Common::merge_geometry", "name": f"merge_{port}"},
                              {"type": "Core::Array::array_size", "name": f"size_{port}"}]
            spec["outputs"][f"{port}__count"] = "long"
            spec["outputs"][f"{port}__merged"] = "Object"
            spec["connections"] += [[f"c.{port}", f"merge_{port}.geometry"], [f"c.{port}", f"size_{port}.array"],
                                    [f"size_{port}.size", f".{port}__count"],
                                    [f"merge_{port}.merged", f".{port}__merged"]]
        else:
            continue
        readable.add(port)
    if frames:
        start, end = frames
        spec["frames"] = [start, end]
        spec["sample_frames"] = sorted({start, (start + end) // 2, end})
    return spec, readable




def verify(path: Path, compound_name: str | None, sets: list[str], fast: bool,
           frames: list[int] | None = None) -> dict:
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    report = {"file": str(path), "stages": {}}

    static = validate_native_graph.validate_document(document)
    report["stages"]["static"] = {
        "ok": not static["errors"] and not static["evidence_warnings"],
        "errors": static["errors"][:20], "evidence_warnings": static["evidence_warnings"][:20],
        "stats": static["stats"]}
    if static["errors"] and any(e["code"] == "NOT_NATIVE_COMPOUND" for e in static["errors"]):
        report["verdict"] = "FAILED"
        return report

    compound = public_compound(document, compound_name)
    name = compound["name"]
    report["compound"] = name
    outputs = {p["portName"]: p.get("portType", "auto") for p in compound.get("ports", [])
               if p.get("portDirection") == "output"}

    scratch = tempfile.TemporaryDirectory(prefix="verify_compound_")
    clash = installed_names().get(name)
    if clash:
        path, name = renamed_copy(document, name, Path(scratch.name))
        report["note"] = (f"{report['compound']} is already installed ({clash}); verified a temporary copy "
                          f"named {name}, so the installed one doesn't shadow or clash with it")

    compiled, _ = bifcmd_check.check(path, name, False, [], None, False, 300)
    report["stages"]["compile"] = {key: compiled.get(key) for key in ("ok", "stages", "errors", "warnings", "fatal")
                                   if compiled.get(key) is not None}

    if fast:
        report["stages"]["evaluate"] = {"skipped": "--fast"}
    elif not compiled.get("ok"):
        report["stages"]["evaluate"] = {"skipped": "compile failed"}
    else:
        spec, readable = evaluation_spec(name, outputs, sets, frames)
        session, _ = bifrost_headless.run([spec], timeout=900, library_files=[str(path)])
        graph = (session.get("graphs") or [{}])[0]
        report["stages"]["evaluate"] = {
            "ok": bool(graph.get("ok")) and not session.get("fatal"),
            "outputs": graph.get("outputs", {}),
            "frames": graph.get("frames"),
            "not_read": sorted(set(outputs) - readable),
            "failed_steps": [s for s in graph.get("steps", []) if "error" in s],
            "log": graph.get("log", [])[:20],
            "fatal": session.get("fatal"),
            "timing": graph.get("timing", {})}

    scratch.cleanup()
    stages = report["stages"]
    if any(stage.get("ok") is False for stage in stages.values()):
        report["verdict"] = "FAILED"
    elif any("skipped" in stage for stage in stages.values()):
        report["verdict"] = "PARTIAL"
    else:
        report["verdict"] = "VERIFIED"
    return report


def summarize(report: dict) -> str:
    lines = [f"{report['verdict']}  {report.get('compound', '')}  ({report['file']})"]
    if report.get("note"):
        lines.append(f"  note: {report['note']}")
    for stage, data in report["stages"].items():
        if "skipped" in data:
            lines.append(f"  {stage:9} skipped ({data['skipped']})")
            continue
        lines.append(f"  {stage:9} {'ok' if data.get('ok') else 'FAIL'}")
        for item in data.get("errors", [])[:10]:
            lines.append(f"      error: {item if isinstance(item, str) else item['code'] + ' ' + item['path'] + ': ' + item['detail']}")
        for item in data.get("evidence_warnings", [])[:10]:
            lines.append(f"      gap: {item['code']} {item['path']}: {item['detail']}")
        if data.get("fatal"):
            lines.append(f"      fatal: {data['fatal']}")
        for step in data.get("failed_steps", []):
            lines.append(f"      step failed: {step['step']}: {step.get('error')}")
        for line in data.get("log", [])[:10]:
            lines.append(f"      maya: {line}")
        if data.get("frames"):
            for frame, values in data["frames"].items():
                lines.append(f"      frame {frame}:")
                lines += [f"        {port} = {json.dumps(value)}" for port, value in values.items()]
        else:
            for port, value in data.get("outputs", {}).items():
                lines.append(f"      {port} = {json.dumps(value)}")
        if data.get("not_read"):
            lines.append(f"      not read (array or custom types): {', '.join(data['not_read'])}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Static, compile and headless-evaluate checks for a compound file.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--compound", help="top-level compound to verify when the file has several")
    parser.add_argument("--set", action="append", default=[], metavar="PORT=VALUE",
                        help="compound input value for the evaluate stage")
    parser.add_argument("--fast", action="store_true", help="skip the headless evaluate stage")
    parser.add_argument("--frames", nargs=2, type=int, metavar=("START", "END"),
                        help="simulate this frame range and read outputs at start, middle and end")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    report = verify(args.file.resolve(), args.compound, args.set, args.fast, args.frames)
    print(json.dumps(report, indent=1, default=repr) if args.json else summarize(report))
    return 0 if report["verdict"] == "VERIFIED" or (args.fast and report["verdict"] == "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
