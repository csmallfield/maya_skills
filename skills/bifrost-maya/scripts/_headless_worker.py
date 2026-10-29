"""Persistent headless Maya for bifrost_headless.py. Not meant to be called directly.

    mayapy _headless_worker.py STATE_FILE LIBRARY_DIR

Starts Maya once, then serves requests on a localhost socket so each graph
check skips Maya's ~35 s startup. STATE_FILE receives {"pid", "port", ...}
once it is ready. A request is one JSON line:

    {"specs": [...], "library": ["C:/path/compound.json", ...]}

and the reply is one JSON line with the session report plus `output`, the
Maya text printed while serving it (graph markers included). Every graph runs
in a new scene. Library files are copied into LIBRARY_DIR (which the
launcher put on BIFROST_LIB_CONFIG_FILES) and the Bifrost plugin is reloaded,
because Bifrost only reads compound files when the plugin loads. The worker
exits after IDLE_SECONDS without a request, or on {"stop": true}.
"""
import json
import os
import shutil
import socket
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _headless_runner as runner  # noqa: E402

IDLE_SECONDS = 1800


def flush_c_stdio():
    # Maya writes Warning/Error lines through the C runtime; flush it so they land
    # in the log before we read it back.
    try:
        import ctypes
        ctypes.cdll.ucrtbase.fflush(None)
    except Exception:
        pass
    sys.stdout.flush()
    sys.stderr.flush()


def read_log_since(path, offset):
    flush_c_stdio()
    with open(path, "rb") as stream:
        stream.seek(offset)
        return stream.read().decode("utf-8", errors="replace")


def log_size(path):
    flush_c_stdio()
    return os.path.getsize(path)


def load_library(files, library_dir, current):
    """Replace the scratch library with FILES and reload the plugin if it changed."""
    wanted = [(os.path.basename(f), os.path.getmtime(f), os.path.getsize(f)) for f in files]
    if wanted == current:
        return current, 0.0
    start = time.time()
    for name in os.listdir(library_dir):
        os.remove(os.path.join(library_dir, name))
    for index, path in enumerate(files):
        shutil.copyfile(path, os.path.join(library_dir, f"{index:02d}_{os.path.basename(path)}"))
    runner.cmds.file(new=True, force=True)
    runner.cmds.unloadPlugin("bifrostGraph", force=True)
    runner.cmds.loadPlugin("bifrostGraph")
    return wanted, round(time.time() - start, 3)


def serve(state_file, library_dir, log_path):
    info = runner.init_maya()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    server.settimeout(IDLE_SECONDS)
    with open(state_file, "w", encoding="utf-8") as stream:
        json.dump({"pid": os.getpid(), "port": server.getsockname()[1], "log": log_path,
                   "library_dir": library_dir, **info}, stream)
    library = []
    while True:
        try:
            connection, _ = server.accept()
        except socket.timeout:
            break
        with connection:
            connection.settimeout(None)
            data = b""
            while not data.endswith(b"\n"):
                chunk = connection.recv(65536)
                if not chunk:
                    break
                data += chunk
            try:
                request = json.loads(data.decode("utf-8"))
            except ValueError:
                continue
            if request.get("stop"):
                connection.sendall(b'{"stopped": true}\n')
                break
            offset = log_size(log_path)
            session = {"graphs": [], "timing": {}, "bifrost_version": info["bifrost_version"], "worker": True}
            try:
                library, reload_seconds = load_library(request.get("library", []), library_dir, library)
                if reload_seconds:
                    session["timing"]["library_reload"] = reload_seconds
                for index, spec in enumerate(request.get("specs", [])):
                    runner.cmds.file(new=True, force=True)
                    session["graphs"].append(runner.run_graph(index, spec))
            except Exception:
                session["fatal"] = traceback.format_exc()
            session["output"] = read_log_since(log_path, offset)
            connection.sendall(json.dumps(session, default=repr).encode("utf-8") + b"\n")
    try:
        os.remove(state_file)
    except OSError:
        pass


if __name__ == "__main__":
    state, library_dir, log_path = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        serve(state, library_dir, log_path)
    except Exception:
        traceback.print_exc()
    sys.stdout.flush()
    os._exit(0)
