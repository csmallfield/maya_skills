# Native export regression checks

Run from the skill root:

```bash
python -m unittest discover -s tests -v
python scripts/validate_native_graph.py assets/native-examples/ppg_nyc_skyscraper_v3_1_fast.json --strict-evidence
```

The tests include the two historical defects: a graph blueprint cannot satisfy the native-compound contract, and removing the tier-local helper from the working v3.1 file must produce the original scope error even though a parent copy remains. Other cases check endpoint/port errors, dynamic inputs, duplicate records, loop iteration targets, cycles, evidence gaps and separation of PPG work from layout loops.

These are offline Python tests. Passing them does not compile a graph in Maya, resolve runtime overloads, run PPG, test a renderer or measure evaluation speed. The optional baker's passing structural test does not make it user-confirmed. See the example manifest and `references/regression-history.md` for evidence status.

`validation-summary.json` records the package-build check; re-run the suite after changing the validator or examples. Add new source evidence rather than suppressing warnings when a legitimate version-specific external port is absent from the partial evidence catalog.

## Headless Maya

`test_headless_harness.py` checks log parsing and hints offline. Its live test starts `mayapy` and builds two graphs: a cube, and one with a deliberate type error. Run it with:

```bash
BIFROST_HEADLESS_TESTS=1 python -m unittest discover -s tests -p "test_headless_harness.py" -v
```
