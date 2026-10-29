"""Checks on the headless harness.

The offline tests parse canned mayapy output. The live test starts mayapy
(about 50 s) and only runs when BIFROST_HEADLESS_TESTS=1.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bifrost_headless", ROOT / "scripts/bifrost_headless.py")
headless = importlib.util.module_from_spec(spec)
spec.loader.exec_module(headless)

CANNED = """Loading library: VHH
Warning: library noise before any graph
@@BIFROST_GRAPH_START 0
Bifrost: New GraphContainer added to the Workspace.
@@BIFROST_GRAPH_END 0
@@BIFROST_GRAPH_START 1
Bifrost resolve messages:
\tError: while compiling top level compound 'bifrostGraphShape2', around the port 'bifrostGraphShape2.n':
    no promotion exists from a value of type 'Object' to a value of type 'long'
@@BIFROST_GRAPH_END 1
"""


class OfflineTests(unittest.TestCase):
    def session(self):
        return {"graphs": [
            {"ok": True, "steps": [], "node_types": {}},
            {"ok": True, "node_types": {"cube": "Modeling::Primitive::create_mesh_cube"}, "steps": [
                {"step": "add Modeling::Primitive::create_mesh_cubez", "error": "RuntimeError: Maya command error"},
                {"step": "connect cube.no_such_port -> .n", "error": "RuntimeError: Maya command error"},
            ]},
        ]}

    def test_compile_errors_fail_only_their_graph(self):
        session = self.session()
        headless.attach_logs(session, CANNED)
        self.assertTrue(session["graphs"][0]["ok"])
        self.assertNotIn("log", session["graphs"][0])
        self.assertFalse(session["graphs"][1]["ok"])
        self.assertEqual(session["graphs"][1]["compile_errors"], 1)
        self.assertTrue(any("no promotion exists" in line for line in session["graphs"][1]["log"]))

    def test_startup_noise_is_ignored(self):
        session = self.session()
        headless.attach_logs(session, CANNED)
        logs = sum((g.get("log", []) for g in session["graphs"]), [])
        self.assertFalse(any("library noise" in line for line in logs))

    def test_hints_for_unknown_node_and_port(self):
        session = self.session()
        headless.add_hints(session)
        add, connect = session["graphs"][1]["steps"]
        self.assertIn("not in the installed library index", add["hint"])
        self.assertIn("has no port 'no_such_port'", connect["hint"])


@unittest.skipUnless(os.environ.get("BIFROST_HEADLESS_TESTS") == "1", "set BIFROST_HEADLESS_TESTS=1 to run mayapy")
class LiveTests(unittest.TestCase):
    def test_cube_and_type_error(self):
        specs = [
            {"nodes": [{"type": "Modeling::Primitive::create_mesh_cube", "name": "cube"}],
             "values": {"cube.width": "3"}, "outputs": {"mesh": "Object"},
             "connections": [["cube.cube_mesh", ".mesh"]]},
            {"nodes": [{"type": "Modeling::Primitive::create_mesh_cube", "name": "cube"}],
             "outputs": {"n": "long"}, "connections": [["cube.cube_mesh", ".n"]]},
        ]
        session, code = headless.run(specs, timeout=600)
        self.assertEqual(code, 1)
        cube, bad = session["graphs"]
        self.assertTrue(cube["ok"])
        self.assertEqual(cube["outputs"]["mesh"]["vertices"], 8)
        self.assertEqual(cube["outputs"]["mesh"]["bbox"][0], -1.5)
        self.assertFalse(bad["ok"])
        self.assertGreaterEqual(bad.get("compile_errors", 0), 1)


@unittest.skipUnless(os.environ.get("BIFROST_HEADLESS_TESTS") == "1", "set BIFROST_HEADLESS_TESTS=1 to run bifcmd")
class BifcmdTests(unittest.TestCase):
    """The helper-scope defect from regression-history.md must fail at compile, as it did in Maya."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "scripts"))
        import bifcmd_check
        cls.check = staticmethod(bifcmd_check.check)

    def write(self, document, name):
        import tempfile
        folder = Path(tempfile.mkdtemp(prefix="bifcmd_test_"))
        path = folder / name
        path.write_text(json.dumps(document), encoding="utf-8")
        return path

    def skyscraper(self, suffix):
        document = json.loads((ROOT / "assets/native-examples/ppg_nyc_skyscraper_v3_1_fast.json").read_text(encoding="utf-8-sig"))
        document["compounds"][0]["name"] += suffix  # an installed duplicate name crashes bifcmd
        return document

    def test_scope_bug_fails_compile_and_intact_file_compiles(self):
        good = self.skyscraper("__test_ok")
        result, code = self.check(self.write(good, "ok.json"), good["compounds"][0]["name"], False, [], None, False, 300)
        self.assertEqual(code, 0, result)

        bad = self.skyscraper("__test_scope")

        def walk(scope):
            yield scope
            for child in scope.get("compounds", []) or []:
                yield from walk(child)
        tier = next(s for s in walk(bad["compounds"][0]) if s.get("name") == "nyc_for_each_tier")
        tier["compounds"] = [c for c in tier["compounds"] if c.get("name") != "nyc_affine_box_points"]
        result, code = self.check(self.write(bad, "bad.json"), bad["compounds"][0]["name"], False, [], None, False, 300)
        self.assertEqual(code, 1)
        self.assertFalse(result["stages"]["compilationOk"])
        self.assertTrue(any("unknown node definition 'nyc_affine_box_points'" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
