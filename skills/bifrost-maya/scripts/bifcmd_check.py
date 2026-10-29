#!/usr/bin/env python3
"""Load, compile and optionally run a compound JSON file with Bifrost's bifcmd.exe.

    bifcmd_check.py FILE.json [--compound-name NS::name] [--run] [--set-port NAME VALUE] [--frames A B] [--json]
    bifcmd_check.py --compound-name NS::name       # an installed compound, from the user's libraries

bifcmd loads the file directly (no install, no Maya, about 10 s). The default
is a compile check (`--list-ports`); `--run` also executes and summarizes the
outputs. Complex graphs can crash bifcmd while executing even when they run
fine in Maya, so treat a run crash as "use bifrost_headless.py", not as a
broken file.

Warnings are filtered to the ones that mention a compound defined in FILE, so
noise from the user's installed libraries stays out. The USD pack loads when
MayaUSD's USD libraries matching the pack version are installed: they, and
Maya's bin folder, go on PATH for bifcmd. Otherwise, or with --no-usd, the
pack is disabled and USD compounds can't be checked.

Exit code: 0 loaded and compiled (and ran, with --run), 1 a stage failed,
2 bifcmd crashed or could not start. Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_BIFROST = Path(r"C:\Program Files\Autodesk\Bifrost\Maya2026\3.0.0.0\bifrost")
STAGES = ("configFilesLoadedOk", "parametersOk", "definitionFilesLoadedOk", "compoundLoadedOk",
          "compilationOk", "executionOk")


def bifrost_root() -> Path:
    root = Path(os.environ.get("BIFROST_ROOT", DEFAULT_BIFROST))
    if not (root / "bin" / "bifcmd.exe").is_file():
        sys.exit(f"bifcmd.exe not found under {root}; set BIFROST_ROOT to the install's bifrost folder.")
    return root


def usd_environment(root: Path) -> dict | None:
    """PATH and plugin-path additions that let bifcmd load the USD pack, or None.

    The pack in bifrost/packs/usd_pack/<ver> needs MayaUSD's USD_<ver> libraries
    and Maya's own bin folder; nothing extra is downloaded.
    """
    packs = sorted((root / "packs" / "usd_pack").glob("*/bin"), key=lambda p: [int(x) for x in re.findall(r"\d+", p.parent.name)])
    maya_bin = Path(os.environ.get("MAYA_LOCATION", r"C:\Program Files\Autodesk\Maya2026")) / "bin"
    for pack in reversed(packs):
        version = pack.parent.name
        for usd in sorted(Path(r"C:\Program Files\Autodesk\MayaUSD").glob(f"*/*/mayausd/USD_{version}"), reverse=True):
            if (usd / "lib").is_dir() and maya_bin.is_dir():
                return {"path": [usd / "lib", usd / "bin", maya_bin], "plugins": usd / "lib" / "usd", "version": version}
    return None


def defined_compounds(path: Path) -> list[str]:
    def walk(scope):
        yield scope.get("name", "")
        for child in scope.get("compounds", []) or []:
            yield from walk(child)
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    return [name for top in document.get("compounds", []) for name in walk(top) if name]


def check(path: Path | None, compound: str | None, run: bool, set_ports: list[list[str]],
          frames: list[str] | None, no_usd: bool, timeout: float) -> tuple[dict, int]:
    root = bifrost_root()
    env = dict(os.environ)
    paths = [root / "bin", root / "thirdparty" / "bin"]
    usd = None if no_usd else usd_environment(root)
    if usd:
        paths += usd["path"]
        env["PXR_PLUGINPATH_NAME"] = os.pathsep.join(filter(None, [str(usd["plugins"]), env.get("PXR_PLUGINPATH_NAME")]))
        env.pop("BIFROST_DISABLE_PACKS", None)
    else:
        env["BIFROST_DISABLE_PACKS"] = "usd_pack"
    env["PATH"] = os.pathsep.join([*map(str, paths), env.get("PATH", "")])
    names = defined_compounds(path) if path else [compound]
    with tempfile.TemporaryDirectory(prefix="bifcmd_check_") as tmp:
        log = Path(tmp) / "log.json"
        # With no file, bifcmd compiles the compound from the installed libraries.
        command = [str(root / "bin" / "bifcmd.exe"), *([str(path)] if path else []), "--log-file", str(log)]
        if compound:
            command += ["--compound-name", compound]
        if not run:
            command.append("--list-ports")
        for name, value in set_ports:
            command += ["--set-port", name, value]
        if frames:
            command += ["--frames", *frames]
        try:
            proc = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                  timeout=timeout, env=env, cwd=tmp)
        except subprocess.TimeoutExpired:
            return {"ok": False, "fatal": f"bifcmd timed out after {timeout}s"}, 2
        if not log.is_file():
            return {"ok": False, "fatal": f"bifcmd exited {proc.returncode} without a log (crash)",
                    "output_tail": (proc.stdout + proc.stderr).strip().splitlines()[-10:]}, 2
        try:
            raw = json.loads(log.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return {"ok": False, "fatal": f"bifcmd exited {proc.returncode} with an empty or partial log (crash)",
                    "output_tail": (proc.stdout + proc.stderr).strip().splitlines()[-10:]}, 2
    report = raw.get("report", {})
    stages = {key: raw.get(key, report.get(key)) for key in STAGES}
    if not run:
        stages.pop("executionOk")
    messages = report.get("messages", {})
    bifrost = messages.get("bifrost", {})
    relevant = lambda text: any(name in text for name in names)
    result = {
        "file": str(path) if path else "(installed library)",
        "compounds_defined": names,
        "mode": "run" if run else "compile",
        "stages": stages,
        "ok": all(stages.values()),
        "errors": bifrost.get("error", []) + bifrost.get("critical", []) + messages.get("bifcmd", {}).get("error", []),
        "warnings": [w for w in bifrost.get("warning", []) if relevant(w)],
        "ports": report.get("inputPorts", []) if not run else None,
        "outputs": [{"name": p.get("name"), "type": p.get("type"), "value": p.get("value")}
                    for p in report.get("outputPorts", [])],
        "exit_code": proc.returncode,
        "usd_pack": usd["version"] if usd else None,
    }
    if proc.returncode < 0 or proc.returncode > 255:
        result["ok"] = False
        result["fatal"] = f"bifcmd crashed (exit {proc.returncode})"
        return result, 2
    return result, 0 if result["ok"] else 1


def compact(value: str) -> str:
    """Shorten bifcmd's geometry dump to component counts and point bounds."""
    counts = re.findall(r"(\w+_component): count: (\d+)", value)
    if not counts:
        return value.replace("\n", " ")[:300]
    parts = [f"{name.removesuffix('_component')} {count}" for name, count in counts]
    bounds = re.search(r"point_position:[^{]*\{\s*min: (\{[^}]*\})\s*max: (\{[^}]*\})", value)
    if bounds:
        parts.append(f"point_position {bounds.group(1)} .. {bounds.group(2)}")
    return ", ".join(parts)


def summarize(result: dict) -> str:
    lines = [f"{'PASS' if result.get('ok') else 'FAIL'}  bifcmd {result.get('mode', '')}  {result.get('file', '')}"]
    if result.get("fatal"):
        lines.append(f"  FATAL: {result['fatal']}")
        lines += [f"    {line}" for line in result.get("output_tail", [])]
    for stage, value in (result.get("stages") or {}).items():
        lines.append(f"  {'ok ' if value else 'NO '} {stage}")
    for error in result.get("errors", [])[:20]:
        lines.append(f"  error: {error}")
    for warning in result.get("warnings", [])[:20]:
        lines.append(f"  warning: {warning}")
    for output in result.get("outputs", []):
        lines.append(f"  output {output['name']} [{output['type']}]: {compact(str(output.get('value', '')))}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile-check or run a compound file with bifcmd.")
    parser.add_argument("file", type=Path, nargs="?", help="compound file; omit to check an installed compound by --compound-name")
    parser.add_argument("--compound-name", help="compound to check when the file defines several")
    parser.add_argument("--run", action="store_true", help="execute too, not just compile")
    parser.add_argument("--set-port", nargs=2, action="append", default=[], metavar=("NAME", "VALUE"))
    parser.add_argument("--frames", nargs=2, metavar=("BEGIN", "END"))
    parser.add_argument("--no-usd", action="store_true", help="disable the USD pack even if MayaUSD is installed")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if not args.file and not args.compound_name:
        parser.error("give a file or --compound-name")
    result, code = check(args.file.resolve() if args.file else None, args.compound_name, args.run, args.set_port, args.frames,
                         args.no_usd, args.timeout)
    print(json.dumps(result, indent=1) if args.json else summarize(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
