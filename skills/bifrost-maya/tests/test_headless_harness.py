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


class BifcmdMultiInputTests(BifcmdTests):
    def compound(self, literal):
        c = {"name": f"Claude::Tests::multi_{'literal' if literal else 'valuenode'}", "metadata": [],
             "ports": [{"portName": "x", "portDirection": "input", "portType": "float", "portDefault": "5f"},
                       {"portName": "y", "portDirection": "output", "portType": "float"}],
             "compoundNodes": [{"nodeName": "times_two", "nodeType": "Core::Math::multiply", "multiInPortNames": ["in_0", "in_1"]}],
             "connections": [{"source": ".x", "target": "times_two.first.in_0"}, {"source": "times_two.output", "target": ".y"}],
             "values": [], "libraryDependencies": {"Amino": "2.15.0.9"}}
        if literal:
            c["values"].append({"valueName": "times_two.first.in_1", "valueType": "float", "value": "2f"})
        else:
            c["compoundNodes"].append({"nodeName": "two", "valueType": "float"})
            c["values"].append({"valueName": "two.value", "valueType": "float", "value": "2f"})
            c["connections"].append({"source": "two.output", "target": "times_two.first.in_1"})
        return {"header": {"metadata": [{"metaName": "adskFileFormatVersion", "metaValue": "100L"}]},
                "namespaces": [], "types": [], "compounds": [c]}

    def test_literal_on_multi_input_child_is_ignored(self):
        results = {}
        for literal in (True, False):
            document = self.compound(literal)
            result, code = self.check(self.write(document, "m.json"), document["compounds"][0]["name"], True, [], None, False, 300)
            self.assertEqual(code, 0, result)
            results[literal] = next(o["value"] for o in result["outputs"] if o["name"] == "y")
        self.assertEqual(float(results[True]), 0.0)    # the literal 2 is dropped
        self.assertEqual(float(results[False]), 10.0)  # a wired value node works

    test_scope_bug_fails_compile_and_intact_file_compiles = None


class InstallTests(unittest.TestCase):
    def test_install_refuses_without_yes(self):
        import subprocess, tempfile
        folder = tempfile.mkdtemp(prefix="install_test_")
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/install_compound.py"),
                                 str(ROOT / "assets/native-examples/cs_green_goo_v5(1).json"), "--folder", folder],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing", result.stdout)
        self.assertEqual(list(Path(folder).iterdir()), [])


@unittest.skipUnless(os.environ.get("BIFROST_HEADLESS_TESTS") == "1", "set BIFROST_HEADLESS_TESTS=1 to run mayapy")
class Phase6LiveTests(unittest.TestCase):
    def test_worker_repeat_runs_are_fast(self):
        spec = {"nodes": [{"type": "Modeling::Primitive::create_mesh_cube", "name": "cube"}],
                "outputs": {"mesh": "Object"}, "connections": [["cube.cube_mesh", ".mesh"]]}
        headless.run([spec], timeout=600)
        start = __import__("time").time()
        session, code = headless.run([spec], timeout=600)
        self.assertEqual(code, 0, session)
        self.assertEqual(session["graphs"][0]["outputs"]["mesh__points"], 8)
        self.assertLess(__import__("time").time() - start, 15)

    def test_simulation_advances_over_frames(self):
        # Without async off and per-frame pulls, every sample returned the frame-1 state.
        spec = {"nodes": [{"type": "Graphs::MPM::sand_pile", "name": "sim"},
                          {"type": "Modeling::Common::merge_geometry", "name": "merge"},
                          {"type": "Geometry::Points::get_bounding_box", "name": "bounds"}],
                "outputs": {"bounds": "Object"},
                "connections": [["sim.out_geometry", "merge.geometry"], ["merge.merged", "bounds.points"],
                                ["bounds.aabb_mesh", ".bounds"]],
                "frames": [1, 6], "sample_frames": [1, 6], "point_counts": False}
        session, code = headless.run([spec], timeout=900)
        self.assertEqual(code, 0, session)
        frames = session["graphs"][0]["frames"]
        top = lambda f: frames[f]["bounds"]["bbox"][4]
        self.assertLess(top("6"), top("1") - 0.5)

    def test_usd_compound_compiles_in_bifcmd(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import bifcmd_check
        if not bifcmd_check.usd_environment(bifcmd_check.bifrost_root()):
            self.skipTest("MayaUSD not installed")
        # A USD compound with typed ports (create_usd_stage has an auto input bifcmd cannot compile alone).
        result, code = bifcmd_check.check(None, "User::Compounds::CJS_simple_usd_loader", False, [], None, False, 300)
        self.assertEqual(code, 0, result)
        self.assertTrue(result["usd_pack"])


if __name__ == "__main__":
    unittest.main()
