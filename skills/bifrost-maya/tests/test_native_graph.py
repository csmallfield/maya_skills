"""Regression tests for authored native JSON, not Maya/Bifrost execution."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_native_graph import load_evidence, validate_document


def passthrough():
    return {"header": {"metadata": [{"metaName": "adskFileFormatVersion", "metaValue": "100L"}]},
            "namespaces": [], "types": [], "compounds": [{"name": "Test::passthrough",
            "ports": [{"portName": "x", "portDirection": "input", "portType": "float"},
                      {"portName": "y", "portDirection": "output", "portType": "float"}],
            "compounds": [], "compoundNodes": [], "values": [],
            "connections": [{"source": ".x", "target": ".y"}]}]}


def child(c, name):
    return next(x for x in c["compounds"] if x["name"] == name)


class NativeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = load_evidence()
        cls.good = json.loads((ROOT / "assets/native-examples/ppg_nyc_skyscraper_v3_1_fast.json").read_text())

    def check(self, d):
        return validate_document(d, self.evidence)

    def assert_error(self, d, code):
        self.assertIn(code, [e["code"] for e in self.check(d)["errors"]])

    def test_01_user_confirmed_v3_1(self):
        report = self.check(self.good)
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["evidence_warnings"])
        self.assertEqual(12, report["stats"]["local_calls"])
        self.assertEqual(11, report["stats"]["definition_scopes"])
        self.assertEqual(183, report["stats"]["stored_nodes"])

    def test_02_original_scope_failure_reproduced(self):
        d = copy.deepcopy(self.good)
        layout = child(d["compounds"][0], "nyc_instance_layout")
        tier = child(layout, "nyc_for_each_tier")
        tier["compounds"] = [c for c in tier["compounds"] if c["name"] != "nyc_affine_box_points"]
        self.assertTrue(any(c["name"] == "nyc_affine_box_points" for c in layout["compounds"]))
        errors = self.check(d)["errors"]
        self.assertEqual(1, len(errors))
        self.assertEqual("UNRESOLVED_LOCAL_TYPE", errors[0]["code"])
        self.assertIn("tier_trim_records -> nyc_affine_box_points", errors[0]["detail"])

    def test_03_blueprint_is_not_native(self):
        self.assert_error({"name": "skyscraper", "nodes": [], "connections": []}, "NOT_NATIVE_COMPOUND")

    def test_04_working_format_example(self):
        d = json.loads((ROOT / "assets/native-examples/cs_green_goo_v5(1).json").read_text())
        report = self.check(d)
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["evidence_warnings"])

    def test_05_optional_baker_structural_only(self):
        d = json.loads((ROOT / "assets/native-examples/ppg_nyc_skyscraper_bake_v3.json").read_text())
        report = self.check(d)
        self.assertEqual([], report["errors"])
        self.assertEqual([], report["evidence_warnings"])

    def test_06_duplicate_target(self):
        d = passthrough();d["compounds"][0]["connections"] *= 2
        self.assert_error(d, "DUPLICATE_TARGET")

    def test_07_wrong_interface_direction(self):
        d = passthrough();d["compounds"][0]["connections"][0]["source"] = ".y"
        self.assert_error(d, "INTERFACE_DIRECTION")

    def test_08_missing_endpoint(self):
        d = passthrough();d["compounds"][0]["connections"][0]["source"] = "missing.output"
        self.assert_error(d, "UNKNOWN_ENDPOINT_NODE")

    def test_09_undriven_output(self):
        d = passthrough();d["compounds"][0]["connections"] = []
        self.assert_error(d, "UNDRIVEN_OUTPUT")

    def test_10_fake_local_type(self):
        d = passthrough();d["compounds"][0]["compoundNodes"] = [{"nodeName": "invented", "nodeType": "do_magic"}]
        self.assert_error(d, "UNRESOLVED_LOCAL_TYPE")

    def test_11_unknown_external_is_evidence_gap(self):
        d = passthrough();d["compounds"][0]["compoundNodes"] = [{"nodeName": "invented", "nodeType": "MadeUp::do_magic"}]
        report = self.check(d)
        self.assertIn("UNKNOWN_EXTERNAL_TYPE", [x["code"] for x in report["evidence_warnings"]])

    def test_12_primitive_summary_port_is_not_accepted(self):
        d = copy.deepcopy(self.good)
        lib = child(d["compounds"][0], "nyc_shared_module_library")
        v = next(v for v in lib["values"] if v["valueName"] == "one_unit_cube.width")
        v["valueName"] = "one_unit_cube.size"
        warnings = self.check(d)["evidence_warnings"]
        self.assertTrue(any(x["code"] == "UNOBSERVED_EXTERNAL_PORT" and "create_mesh_cube.size" in x["detail"] for x in warnings))

    def test_13_fan_child_and_missing_declaration(self):
        for remove_all in (False, True):
            with self.subTest(remove_all=remove_all):
                d = copy.deepcopy(self.good)
                n = next(n for n in d["compounds"][0]["compoundNodes"] if n.get("nodeType") == "Geometry::Instances::set_instance_geometry")
                if remove_all:
                    n.pop("fanInPortNames")
                else:
                    for key in n["fanInPortNames"]:n["fanInPortNames"][key] = []
                self.assert_error(d, "UNDECLARED_FAN_IN_CHILD")

    def test_14_bad_loop_iteration_port(self):
        d = copy.deepcopy(self.good)
        tier = child(child(d["compounds"][0], "nyc_instance_layout"), "nyc_for_each_tier")
        tier["ports"][0]["portType"] = "float"
        self.assert_error(d, "NON_ARRAY_ITERATION_TARGET")

    def test_15_typo_in_local_port(self):
        d = copy.deepcopy(self.good)
        edge = next(e for e in d["compounds"][0]["connections"] if e["target"].startswith("dimensions."))
        edge["target"] = "dimensions.not_a_real_port"
        self.assert_error(d, "UNKNOWN_LOCAL_PORT")

    def test_16_duplicate_node_and_port(self):
        d = copy.deepcopy(self.good);c = d["compounds"][0]
        c["compoundNodes"].append(copy.deepcopy(c["compoundNodes"][0]))
        c["ports"].append(copy.deepcopy(c["ports"][0]))
        self.assert_error(d, "DUPLICATE_NODE")
        self.assert_error(d, "DUPLICATE_PORT")

    def test_17_local_dataflow_cycle(self):
        d = passthrough();c = d["compounds"][0]
        helper = copy.deepcopy(c);helper["name"] = "helper"
        c["compounds"] = [helper]
        c["compoundNodes"] = [{"nodeName": "a", "nodeType": "helper"}, {"nodeName": "b", "nodeType": "helper"}]
        c["connections"] = [{"source": "a.y", "target": "b.x"}, {"source": "b.y", "target": "a.x"}, {"source": "a.y", "target": ".y"}]
        self.assert_error(d, "LOCAL_DATAFLOW_CYCLE")

    def test_18_missing_version(self):
        d = passthrough();d["header"]["metadata"] = []
        self.assert_error(d, "MISSING_FORMAT_VERSION")

    def test_19_native_json_roundtrip(self):
        self.assertEqual(self.good, json.loads(json.dumps(self.good)))

    def test_20_no_ppg_in_layout_loop(self):
        def visit(c, inside=False):
            inside = inside or "forEachCompound" in c
            if inside:
                self.assertFalse(any(n.get("nodeType", "").startswith("PPG::") for n in c.get("compoundNodes", [])))
            for ch in c.get("compounds", []):visit(ch, inside)
        visit(self.good["compounds"][0])


if __name__ == "__main__":
    unittest.main()
