# Bifrost Maya skill - phase 5 real-task testing, 2026-10-29

- New rule: Bifrost drops a literal on a multi-input child port (`multiply.first.in_1`) and treats it as 0. `validate_native_graph.py` reports `MULTI_INPUT_CHILD_LITERAL` as an error. This was the root cause of both bugs in `cg_flat_layout_v001`, and it is a latent defect in the v3.1 skyscraper (`minimum_opening_dimension`). There is an offline test, plus a live bifcmd proof (literal gives 0, a wired value node gives 10).
- `verify_compound.py` now reads `array<Object>` outputs: it merges each one (`merge_geometry`) and counts its elements (`array_size`). It also places the compound as a node, and `--set` passes literal input values.
- `bifrost_headless.py`: `node.port[]` targets make a fan-in child, following Autodesk's `connect_to_fanin_port`. `uint`, `ulong`, `uchar` and `ushort` are now read as scalars.
- `search_graph_examples.py` now ranks by name, then category and description, then node types, then capped docs, with stopwords. The inspect and search scripts now print UTF-8.
- SKILL.md: expose few input ports (the user noted Astra promoted every option to a port; Autodesk's examples expose a median of 0); look up ports before writing specs; predict outputs before verifying; PPG selects by its own face tags; the fan-in and playblast recipes; the multi-input literal rule. Regression history adds Cases E and F and the three test tasks.

# Bifrost Maya skill - 3.0 verification and PPG 2.80, 2026-10-29

- `scripts/verify_compound.py`: one verdict (VERIFIED / PARTIAL / FAILED) from three stages: static validation, bifcmd compile, and headless evaluation that reads outputs. It renames installed duplicates, since a duplicate name crashes bifcmd.
- `scripts/bifcmd_check.py`: compiles or runs a compound file, or an installed compound by name, with bifcmd. Filters library noise from the log and summarizes geometry outputs.
- `scripts/scan_compounds.py`: compile-checks every installed compound in a folder.
- `validate_native_graph.py`: ports on shipped nodes are now checked against the exact 3.0 index, so an unknown port is an error (`UNKNOWN_LIBRARY_PORT`), and renamed 2.x node types give a warning. Fixed two false errors that affected Autodesk's own graphs: untyped iteration targets, and the implicit `looping_condition` of do-while loops. All 105 shipped 3.0 graphs now pass, and a test covers that.
- Compound corpus rebuilt with the installed PPG 2.80 beta1 in place of 2.0 (`references/ppg-2.0-vs-2.80.md` lists the changes). `parse_compounds.py` now picks up the PPG version from the folder name.
- Opt-in bifcmd regression: the helper-scope defect fails at compile with Maya's own error, and the intact skyscraper compiles.

# Bifrost Maya skill - Maya connection, 2026-10-29

- `scripts/maya_exec.py`: runs Python in live Maya over the command port. Returns the result, stdout and traceback as JSON. Source goes through a temp file, so the port's buffer size can't truncate it.
- `scripts/bifrost_headless.py` and `_headless_runner.py`: build and evaluate graph specs in a separate mayapy, so crashes are isolated. Reports steps, outputs, compile errors, hints and timing. Runs batches in one session.
- `references/maya-graph-commands.md`: the verified recipe and command reference, taken from Autodesk's own scripts and tested headless and live on 3.0. Records the crash (`createOutputPort` on the graph root) and the fact that type errors print instead of raising.
- The v3.1 skyscraper evaluates headless on 3.0 (`bay_count` 832, `total_height` 166.9).
- `tests/test_headless_harness.py`: offline log and hint parsing, plus an opt-in mayapy test.

# Bifrost Maya skill - Claude port, 2026-10-29

## Ported from the Astra (ChatGPT) skill
- Same rules, corpora, native examples, scripts and tests; removed `agents/openai.yaml`.
- SKILL.md rewritten for Claude around a new evidence order.

## Installed-library node index (Bifrost 3.0.0.0)
- `scripts/build_node_index.py` reads the shipped `resources/*/jsonLibs`, the newest USD pack, changesets and ENU docs.
- `references/bifrost-3.0.0.0/`: 2,020 nodes (1,227 public) with exact ports, types, defaults and overload counts; 30 built-ins with observed ports; 372 enum/struct types; 127 renames.
- `scripts/node_info.py`: lookup, search, shipped docs, exact overloads, types and renames.
- The condensed `nodes-*.md` summaries are demoted to discovery only.
- `tests/test_node_index.py`: cube ports, built-ins, renames, enums, and the bundled examples resolving in 3.0.

# Bifrost Maya skill update - 2026-09-18

## Native compound delivery
- Make native Bifrost JSON the default for Maya-loadable compound requests; do not substitute graph blueprints.
- Prioritize working native exports and exact compound interfaces over simplified node summaries.
- Preserve target typed literals, dynamic ports, loop serialization, dependencies and local definition scope.
- Add a native-file inspector, a conservative offline validator and regression tests for format/scope failures.

## PPG and procedural building design
- Separate prototype modeling, dimensional layout, retained instancing, shading and optional mesh expansion.
- Prefer supported Relative quad cuts, explicit repetition/counts and deliberate selected-edge/tag semantics.
- Keep independent loops focused on lightweight placement, not repeated detailed topology or growing mesh accumulators.
- Distinguish PPG's supplied merged-copy instance operation from retained native Bifrost instancers.
- Document module-stretch trade-offs, property/scale contracts, diagnostic outputs and performance-test boundaries.

## Sources and examples
- Preserve the existing Autodesk examples and full normalized custom corpus, including PPG and VHH.
- Add all 34 supplied PPG Markdown documents without editing their source text.
- Bundle the unchanged user-confirmed v3.1 graph and original working-format example, plus the optional unconfirmed baker.
- Record v3.1's successful user feedback as qualitative evidence; do not invent measured timings or transcript findings.

This archive is a complete replacement skill, not a patch. It does not install or update a live skill automatically.
