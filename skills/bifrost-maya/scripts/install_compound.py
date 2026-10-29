#!/usr/bin/env python3
"""Install a verified compound file into the user's compounds folder, then optionally reload Bifrost live.

    install_compound.py FILE.json --yes [--reload] [--folder DIR] [--skip-verify] [--frames A B]

Only run this after the user has said to install the file. `--yes` is required
so it is never run by accident. Steps:

1. verify_compound.py (static, compile, evaluate); refuse unless VERIFIED.
2. Copy into the compounds folder (default ~/Autodesk/Bifrost/Compounds). A
   different existing file with the same name is renamed to
   `<name>.bak-<timestamp>.json`, never overwritten.
3. With --reload: Bifrost only reads compound files when its plugin loads, so in
   the live Maya (command port) the plugin is unloaded and reloaded. That needs
   a new scene, so it refuses when the scene has unsaved changes; a saved scene
   is reopened afterwards. Without --reload, the compound appears after the
   next Maya start.

Exit code: 0 installed (and reloaded, if asked), 1 refused or failed.
Python stdlib only.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify_compound  # noqa: E402

RELOAD = r'''
import json
scene = cmds.file(q=True, sceneName=True)
modified = cmds.file(q=True, modified=True)
if modified:
    _result = {"reloaded": False, "reason": "the scene has unsaved changes", "scene": scene or "(untitled)"}
else:
    cmds.file(new=True, force=True)
    cmds.unloadPlugin("bifrostGraph", force=True)
    cmds.loadPlugin("bifrostGraph")
    if scene:
        cmds.file(scene, open=True, force=True)
    namespace, _, short = NAME.rpartition("::")
    _result = {"reloaded": True, "scene": scene or "(untitled)",
               "available": short in (cmds.vnn(nodes=("BifrostGraph", namespace)) or [])}
'''


def live_reload(name: str) -> dict:
    code = f"NAME = {name!r}\n" + RELOAD
    proc = subprocess.run([sys.executable, "-I", str(HERE / "maya_exec.py"), "-"], input=code,
                          capture_output=True, text=True, encoding="utf-8", timeout=600)
    try:
        reply = json.loads(proc.stdout)
    except ValueError:
        return {"reloaded": False, "reason": f"no reply from Maya: {proc.stdout.strip() or proc.stderr.strip()}"}
    if not reply.get("ok"):
        return {"reloaded": False, "reason": reply.get("error")}
    return reply["result"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a verified compound and optionally reload Bifrost live.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--yes", action="store_true", help="confirm: the user asked for this install")
    parser.add_argument("--reload", action="store_true", help="reload the Bifrost plugin in the live Maya afterwards")
    parser.add_argument("--folder", type=Path, default=Path.home() / "Autodesk" / "Bifrost" / "Compounds")
    parser.add_argument("--skip-verify", action="store_true", help="install without verifying (not recommended)")
    parser.add_argument("--frames", nargs=2, type=int, metavar=("START", "END"), help="verify as a simulation")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    source = args.file.resolve()
    if not args.yes:
        print(f"Refusing: pass --yes once the user has asked to install {source.name} into {args.folder}.")
        return 1
    document = json.loads(source.read_text(encoding="utf-8-sig"))
    name = verify_compound.public_compound(document, None)["name"]

    if not args.skip_verify:
        report = verify_compound.verify(source, None, [], False, args.frames)
        print(verify_compound.summarize(report))
        if report["verdict"] != "VERIFIED":
            print(f"Refusing to install: verdict {report['verdict']}.")
            return 1

    args.folder.mkdir(parents=True, exist_ok=True)
    target = args.folder / source.name
    if target.exists():
        if filecmp.cmp(source, target, shallow=False):
            print(f"Already installed, identical: {target}")
        else:
            backup = target.with_name(f"{target.stem}.bak-{time.strftime('%Y%m%d-%H%M%S')}.json")
            target.rename(backup)
            print(f"Existing file kept as {backup}")
    if not target.exists():
        shutil.copyfile(source, target)
        print(f"Installed {name} -> {target}")

    if args.reload:
        result = live_reload(name)
        if not result.get("reloaded"):
            print(f"Not reloaded: {result.get('reason')}. Save the scene and run with --reload again, "
                  "or restart Maya.")
            return 1
        print(f"Reloaded Bifrost in Maya; scene {result['scene']}; {name} available: {result['available']}")
    else:
        print("Maya sees it after the Bifrost plugin reloads (--reload) or the next Maya start.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
