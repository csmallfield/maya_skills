#!/usr/bin/env python3
"""Build and evaluate Bifrost graphs in a separate headless Maya (mayapy).

A crash here kills only the background process, never the user's Maya, so
use this to test node combinations and native compound files before
touching a live session.

    bifrost_headless.py spec.json [--library compound.json ...] [--json] [--timeout SECONDS]

The file holds one spec, or a list of specs that run as separate graphs in
one mayapy session (startup takes about 35 s, so batch related tests).

Spec (every key optional except what you need):

    {
      "nodes": [{"type": "Modeling::Primitive::create_mesh_cube", "name": "cube"}],
      "values": {"cube.width": "3"},
      "outputs": {"mesh": "Object", "count": "long"},
      "connections": [["cube.cube_mesh", ".mesh"]],
      "save_scene": "C:/tmp/test.ma"
    }

- `type` is a fully qualified node or compound name; installed user compounds
  (~/Autodesk/Bifrost/Compounds) load like shipped ones, and `--library FILE`
  loads a compound file that isn't installed (scratch library, this run only).
- `"graph": "Namespace::compound"` unpacks a library compound into an editable
  graph instead of starting empty, as Maya's Bifrost Browser does with
  examples (`bifrostGraph -importGraphAsShape <name>`). Its output ports are
  already there: list them under `outputs` to read them, no connections needed.
- Endpoints are `node.port`; `.port` is the graph boundary (an output port).
- Scalar outputs are read with getAttr. Object outputs are converted with
  `bifrostGraph -createMayaGeometry` and reported as mesh/vertex/face counts.
- Values use Bifrost literal text as the graph editor would accept it.

Reports each step, outputs, timing and the Warning/Error lines Maya printed
while each graph was built and evaluated. Exit code: 0 every step passed,
1 a step failed, 2 mayapy crashed or timed out (the user's Maya session is
unaffected either way). Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def find_mayapy() -> Path:
    candidates = []
    if os.environ.get("MAYA_LOCATION"):
        candidates.append(Path(os.environ["MAYA_LOCATION"]) / "bin" / "mayapy.exe")
    candidates += [Path(r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"),
                   Path("/Applications/Autodesk/maya2026/Maya.app/Contents/bin/mayapy"),
                   Path("/usr/autodesk/maya2026/bin/mayapy")]
    for path in candidates:
        if path.is_file():
            return path
    sys.exit("mayapy not found; set MAYA_LOCATION to the Maya install folder.")


NOISE = ("Bifrost: New GraphContainer", "Bifrost: GraphContainer deleted", "Bifrost resolve messages", "Result:",
         "remark: <unknown>", "warning: <unknown>:0:0: loop not vectorized")  # LLVM JIT remarks


def attach_logs(session: dict, output: str) -> None:
    """Give each graph the Maya output printed between its markers.

    Bifrost compile errors ("Error: while compiling top level compound ...")
    span several lines, so everything in the window is kept except known
    noise. Any compile error fails the graph, since Maya still evaluates the
    rest of the graph and reports zero/default outputs otherwise.
    """
    current = None
    for line in output.splitlines():
        if line.startswith("@@BIFROST_GRAPH_START "):
            current = int(line.split()[1])
            continue
        if line.startswith("@@BIFROST_GRAPH_END "):
            current = None
            continue
        text = line.strip()
        if current is None or current >= len(session["graphs"]) or not text or text.startswith(NOISE):
            continue
        graph = session["graphs"][current]
        log = graph.setdefault("log", [])
        if len(log) < 200 and text not in log:
            log.append(text)
        if text.startswith(("Error", "# Error")):
            graph["ok"] = False
            graph.setdefault("compile_errors", 0)
            graph["compile_errors"] += 1


def add_hints(session: dict) -> None:
    """Maya only says "Maya command error"; explain failed adds and connects from the node index."""
    indexes = sorted(HERE.parent.glob("references/bifrost-*/node-index.json"))
    nodes = json.loads(indexes[-1].read_text(encoding="utf-8")) if indexes else {}
    for graph in session["graphs"]:
        types = graph.get("node_types", {})
        for entry in graph.get("steps", []):
            if "error" not in entry:
                continue
            label = entry["step"]
            if label.startswith("add "):
                name = label[4:]
                if name not in nodes:
                    entry["hint"] = "not in the installed library index (a user compound may still exist); try node_info.py --search"
            elif label.startswith("connect "):
                for end in label[8:].split(" -> "):
                    node, _, port = end.partition(".")
                    record = nodes.get(types.get(node, ""))
                    if node and record and port.split(".")[0] not in {p["name"] for p in record["ports"]}:
                        entry["hint"] = f"{types[node]} has no port '{port}'; see node_info.py {types[node]}"


def library_env(tmp: Path, library_files: list[str]) -> dict:
    """Copy compound files into a scratch library and point Bifrost at it.

    Bifrost only loads compound JSON from configured library folders, when
    the plugin loads. A fresh mayapy per run makes that free, and the user's
    own compounds folder is never written to.
    """
    env = dict(os.environ)
    if not library_files:
        return env
    folder = tmp / "library"
    folder.mkdir()
    for index, name in enumerate(library_files):
        source = Path(name)
        if not source.is_file():
            sys.exit(f"library file not found: {source}")
        (folder / f"{index:02d}_{source.name}").write_bytes(source.read_bytes())
    config = tmp / "scratch_library_config.json"
    config.write_text(json.dumps({"AminoConfigurations": [{
        "vendorName": "Claude", "libraryName": "claude_scratch", "libraryVersion": "1.0",
        "jsonLibs": [{"path": folder.as_posix()}]}]}), encoding="utf-8")
    existing = env.get("BIFROST_LIB_CONFIG_FILES")
    env["BIFROST_LIB_CONFIG_FILES"] = str(config) + (os.pathsep + existing if existing else "")
    return env


def run(specs, timeout: float, library_files: list[str] | None = None) -> tuple[dict, int]:
    with tempfile.TemporaryDirectory(prefix="bifrost_headless_") as tmp:
        spec_path, result_path = Path(tmp) / "spec.json", Path(tmp) / "result.json"
        spec_path.write_text(json.dumps(specs), encoding="utf-8")
        env = library_env(Path(tmp), library_files or [])
        start = time.time()
        try:
            proc = subprocess.run([str(find_mayapy()), "-I", str(HERE / "_headless_runner.py"),
                                   str(spec_path), str(result_path)],
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,  # one stream keeps order
                                  text=True, encoding="utf-8", errors="replace", timeout=timeout, cwd=tmp,
                                  env=env)
        except subprocess.TimeoutExpired:
            return {"graphs": [], "timing": {}, "fatal": f"mayapy timed out after {timeout}s"}, 2
        if not result_path.is_file():
            tail = proc.stdout.strip().splitlines()[-15:]
            return {"graphs": [], "timing": {}, "fatal": "mayapy crashed before writing a report",
                    "exit_code": proc.returncode, "output_tail": tail}, 2
        session = json.loads(result_path.read_text(encoding="utf-8"))
        attach_logs(session, proc.stdout)
        add_hints(session)
        session["timing"]["total"] = round(time.time() - start, 3)
        if session.get("fatal"):
            return session, 2
        return session, 0 if all(graph.get("ok") for graph in session["graphs"]) else 1


def summarize_graph(index: int, report: dict) -> list[str]:
    lines = [f"[{index}] {'PASS' if report.get('ok') else 'FAIL'}"]
    if report.get("fatal"):
        lines.append(f"  FATAL: {report['fatal']}")
    for entry in report.get("steps", []):
        status = "ok " if "error" not in entry else "ERR"
        detail = entry.get("error") or entry.get("result")
        suffix = f"  -> {detail}" if detail not in ("", None, True) else ""
        lines.append(f"  {status} {entry['step']}{suffix}")
        if entry.get("hint"):
            lines.append(f"        hint: {entry['hint']}")
    if report.get("outputs"):
        lines.append("  outputs:")
        lines += [f"    {port}: {json.dumps(value)}" for port, value in report["outputs"].items()]
    if report.get("log"):
        lines.append("  maya log:")
        lines += [f"    {line}" for line in report["log"][:40]]
    if report.get("timing"):
        lines.append("  timing (s): " + ", ".join(f"{k} {v}" for k, v in report["timing"].items()))
    return lines


def summarize(session: dict) -> str:
    lines = [f"Bifrost {session.get('bifrost_version', '?')}"]
    if session.get("fatal"):
        lines.append(f"FATAL: {session['fatal']}")
        lines += [f"  {line}" for line in session.get("output_tail", [])]
    for index, report in enumerate(session.get("graphs", [])):
        lines += summarize_graph(index, report)
    if session.get("timing"):
        lines.append("timing (s): " + ", ".join(f"{k} {v}" for k, v in session["timing"].items()))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Bifrost graph specs in headless Maya.")
    parser.add_argument("spec", help="spec JSON file (one spec or a list), or - for stdin")
    parser.add_argument("--json", action="store_true", help="print the full JSON report")
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--library", action="append", default=[], metavar="FILE",
                        help="compound JSON to load into a scratch library for this run (repeatable)")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    text = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text(encoding="utf-8")
    session, code = run(json.loads(text), args.timeout, args.library)
    print(json.dumps(session, indent=1, default=repr) if args.json else summarize(session))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
