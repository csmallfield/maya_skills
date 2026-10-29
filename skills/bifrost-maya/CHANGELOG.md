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
