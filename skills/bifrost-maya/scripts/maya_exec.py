#!/usr/bin/env python3
"""Run Python inside a live Maya through its command port and print a JSON result.

    maya_exec.py -c "cmds.about(version=True)"
    maya_exec.py script.py
    echo "cmds.ls(type='bifrostGraphShape')" | maya_exec.py -

The code runs with `cmds` (maya.cmds) and `mel` already imported. Like a REPL,
the value of a final expression is returned; otherwise whatever the code
assigns to `_result`. Printed output and tracebacks come back too:

    {"ok": true, "result": ..., "stdout": "...", "error": null}

Maya must have a Python command port open (default localhost:7001):

    cmds.commandPort(name="localhost:7001", sourceType="python")

The source travels through a temp file, so command-port buffer size never
truncates it. Exit code: 0 ok, 1 Maya-side error, 2 connection problem.
Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import tempfile

# Runs inside Maya. Kept to one exec'd string so the payload stays a single line.
RUNNER = r'''
import ast, io, json, sys, traceback
import maya.cmds as cmds, maya.mel as mel
def _claude_run(path, ns):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    ns.setdefault("cmds", cmds); ns.setdefault("mel", mel)
    out, old = io.StringIO(), sys.stdout
    sys.stdout = out
    res = {"ok": True, "result": None, "stdout": "", "error": None}
    try:
        tree = ast.parse(src, path)
        last = tree.body.pop() if tree.body and isinstance(tree.body[-1], ast.Expr) else None
        exec(compile(tree, path, "exec"), ns)
        if last is not None:
            res["result"] = eval(compile(ast.Expression(last.value), path, "eval"), ns)
        elif "_result" in ns:
            res["result"] = ns["_result"]
    except BaseException:
        res["ok"] = False
        res["error"] = traceback.format_exc()
    finally:
        sys.stdout = old
    res["stdout"] = out.getvalue()
    try:
        return json.dumps(res, default=repr)
    except Exception:
        res["result"] = repr(res["result"])
        return json.dumps(res, default=repr)
'''


def send(payload: str, host: str, port: int, timeout: float) -> str:
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(payload.encode("utf-8") + b"\n")
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\x00" in chunk:
                break
    return b"".join(chunks).split(b"\x00", 1)[0].decode("utf-8", errors="replace").rstrip("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Python in Maya via its command port.")
    parser.add_argument("script", nargs="?", help="Python file to run, or - for stdin")
    parser.add_argument("-c", "--code", help="code string to run")
    parser.add_argument("--host", default=os.environ.get("MAYA_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MAYA_PORT", "7001")))
    parser.add_argument("--timeout", type=float, default=120.0, help="seconds to wait for Maya")
    parser.add_argument("--persist", action="store_true",
                        help="run in a namespace kept between calls instead of a fresh one")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.code is not None:
        source = args.code
    elif args.script == "-":
        source = sys.stdin.read()
    elif args.script:
        with open(args.script, encoding="utf-8") as stream:
            source = stream.read()
    else:
        parser.error("give a script path, - for stdin, or -c CODE")

    handle, path = tempfile.mkstemp(prefix="maya_exec_", suffix=".py")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(source)
    namespace = ("__import__('__main__').__dict__.setdefault('_claude_ns', {})" if args.persist
                 else "{'__name__': '__claude__'}")
    payload = (f"(lambda g: (exec({RUNNER!r}, g), g['_claude_run']({path!r}, {namespace}))[1])"
               "(__import__('__main__').__dict__)")
    try:
        reply = send(payload, args.host, args.port, args.timeout)
    except (ConnectionError, socket.timeout, OSError) as exc:
        print(json.dumps({"ok": False, "result": None, "stdout": "",
                          "error": f"Could not reach Maya on {args.host}:{args.port}: {exc}. "
                                   "Is Maya running with the command port open?"}))
        return 2
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    try:
        result = json.loads(reply)
    except json.JSONDecodeError:
        result = {"ok": False, "result": None, "stdout": "", "error": f"Unexpected reply from Maya: {reply!r}"}
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
