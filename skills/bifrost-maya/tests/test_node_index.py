"""Checks on the installed-library node index (references/bifrost-*/)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = sorted(ROOT.glob("references/bifrost-*/node-index.json"))[-1].parent


def load(name: str):
    with (INDEX / name).open(encoding="utf-8") as stream:
        return json.load(stream)


class NodeIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nodes = load("node-index.json")

    def ports(self, name: str, direction: str) -> list[str]:
        return [p["name"] for p in self.nodes[name]["ports"] if p["dir"] == direction]

    def test_cube_ports_match_working_export_not_summary(self):
        # The condensed summary claimed size/divisions/mesh; the export and library agree on these.
        self.assertEqual(self.ports("Modeling::Primitive::create_mesh_cube", "input")[:3], ["length", "width", "height"])
        self.assertEqual(self.ports("Modeling::Primitive::create_mesh_cube", "output"), ["cube_mesh"])

    def test_builtins_are_recorded_with_observed_ports(self):
        entry = self.nodes["Core::Logic::if"]
        self.assertEqual(entry["kind"], "builtin")
        self.assertEqual(set(self.ports("Core::Logic::if", "input")), {"condition", "true_case", "false_case"})

    def test_renamed_names_are_not_builtins(self):
        renames = load("renames.json")
        self.assertEqual(renames["Geometry::Tags::Internal::merge_tags"]["new"], "Geometry::Tags::merge_tag_data")
        self.assertNotIn("Geometry::Tags::Internal::merge_tags", self.nodes)

    def test_enum_members(self):
        types = load("types.json")
        self.assertIn("BlueNoise", types["Modeling::Points::ScatteringMode"]["members"])

    def test_bundled_native_examples_resolve(self):
        custom = set(json.loads((ROOT / "references/compound-data/interface-index.json").read_text(encoding="utf-8")))

        def walk(scope):
            yield scope
            for child in scope.get("compounds", []) or []:
                yield from walk(child)

        for name in ("ppg_nyc_skyscraper_v3_1_fast.json", "cs_green_goo_v5(1).json"):
            document = json.loads((ROOT / "assets/native-examples" / name).read_text(encoding="utf-8-sig"))
            local, used = set(), set()
            for top in document["compounds"]:
                for scope in walk(top):
                    local.add(scope["name"])
                    used.update(n.get("nodeType") for n in scope.get("compoundNodes", []) or [])
            missing = {t for t in used if t and t not in self.nodes and t not in local and t not in custom}
            self.assertEqual(missing, set(), name)

    def test_cli_lookup(self):
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/node_info.py"), "create_mesh_cube"],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cube_mesh: Object", result.stdout)


if __name__ == "__main__":
    unittest.main()
