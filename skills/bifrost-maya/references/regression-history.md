# Native export and PPG building regression history

Use this case history to choose tests and evidence levels, not to replay failed designs.

## Case A: JSON blueprint does not register

The initial delivered `ppg_modular_skyscraper_compound.json` described a graph but was not native Bifrost serialization. Maya did not list it. The user supplied a working `cs_green_goo_v5(1).json`. Rebuilding with its native envelope and compound/node/value conventions resolved registration; the user subsequently confirmed the native building loaded.

Lesson: honor the artifact contract. JSON syntax is not a Bifrost schema. Do not silently deliver a blueprint when asked for a loadable compound. Use actual exports, not the compact node summaries, for exact interfaces. The cube summary's `size/divisions/mesh` was not the working export's `width/length/height/.../cube_mesh`.

Regression: a blueprint input must fail `NOT_NATIVE_COMPOUND`; user-confirmed native examples must pass the supported structural profile. Those results do not compile the graph.

## Case B: large panels are not a floor/window layout

The first native building loaded but produced a few large panels and awkward topology. The screenshot and user feedback establish that result; this record does not claim a uniquely proven root cause for every bad face. Inspect sequence repetition, flexible sizes, selected-edge direction, resulting counts and tag inheritance before layering detailed operations.

The v2 solution used explicit facade grids and PPG details, plus a base, setbacks, crown and entrance. The user confirmed it made a building, but reported slow evaluation and an overly complex graph.

## Case C: prototype work versus repeated facade work

The v3 design modeled one shared PPG bay, kept tier/elevation loops for lightweight layout, and used retained native instancers. A unit cube and parametric records replaced many individual primitive construction branches. Material splitting and normal work moved to prototypes. Optional instance expansion moved to a separate baker.

Source/design distinction: Relative versus Projection and the PPG controls are documented in the supplied Markdown; the merged-copy path is visible in the supplied `PPG_instance` implementation; the prototype/layout split is the design developed here. No YouTube transcript was retrieved. Do not attribute this architecture to a video transcript.

## Case D: a helper exists but is out of scope

The user's next error was `tier_trim_records`, type `nyc_affine_box_points`. The helper was authored and included, but only in the parent `nyc_instance_layout`, not in the nested tier loop that called it. A global set of all definition names incorrectly let the original static checker pass it.

The v3.1 repair put an identical helper directly in `nyc_for_each_tier.compounds`, preserving the parent copy for crown/entrance calls and renaming the public compound. There were no other parsed-graph changes. Stored node definitions rose from 172 to 183; the intended helper calls and modeling work were unchanged.

The user subsequently confirmed v3.1 worked "much much better". Treat this as user-reported successful operation and qualitative improvement in that environment. Do not claim assistant-performed Maya compilation or a measured speedup.

Regression: delete only that tier-local definition from a copy of the bundled v3.1 file. Confirm the validator flags the unresolved local call even though another definition with the same name remains elsewhere. Validate the intact example successfully. Keep this negative test when changing scope handling.

## Case E: literals on multi-input children are dropped (2026-10-29)

`CityGen::Restart::cg_flat_layout_v001` failed to compile on 3.0 with 19 errors like *"no promotion exists from a value of type 'float' to a value of type 'array<float>'"*. Its arrays were built as `multiply(scalar input, constant array)`, with the constant typed as a literal on the multi-input child `multiply.first.in_1`.

Root cause, proven with bifcmd: **Bifrost ignores a literal on a multi-input child port and treats that child as 0.** `multiply(x=5, first.in_1 = 2f)` returns 0, while the same 2 from a wired value node returns 10. Both compile. So:
- An array literal on a child never reaches the node, no auto-looping happens, and the node resolves to `float`. That gives the compile errors.
- A scalar literal on a child silently becomes 0. In the same file every "× 2" in `cg_dimensions` returned 0, so `ground_extent` was 7 instead of 233 and the lot width was 93 instead of 77. It compiled and looked plausible.

Autodesk's 105 shipped graphs never put a literal on a multi-input child. They wire in a value node, or set the fixed `second` port. The fix in `cg_flat_layout_v002` moved all 71 such literals onto value nodes (`{"nodeName": ..., "valueType": ...}` plus `<node>.value`, connected to the child). It is VERIFIED: ground ±1165 units, lot 77 m, 12 road quads, 9 junctions, 16 sidewalks.

The unmodified v3.1 skyscraper has one instance: `nyc_ppg_bay_master/minimum_opening_dimension.first.a = 3.6f` on a `subtract`. So it computes `0 − margins`, the minimum-opening guard never applies, and the building still generates. It hasn't been changed, because it is the user's confirmed file.

Regression: `validate_native_graph.py` reports `MULTI_INPUT_CHILD_LITERAL` as an error. The tests expect exactly this one defect in v3.1. `tests/test_headless_harness.py` has the live 0-vs-10 proof.

Also from this case: `verify_compound.py` didn't read `array<Object>` outputs, so the first VERIFIED said nothing about the geometry. The evaluate stage now merges each array output (`merge_geometry`) and counts its elements (`array_size`).

## Case F: a PPG extrude that selected nothing still VERIFIED (2026-10-29)

`Claude::Tests::ppg_inset_block_v001` put `PPG_extrude.tag_expression = "face_top_tag"` on a `create_mesh_cube`. PPG reads its own face tags, not Bifrost component tags, so nothing was selected and the cube passed through unchanged. Every stage passed and the verdict was VERIFIED. Only the prediction (10 faces, 12 vertices) against the actual output (6 faces, 8 vertices) exposed it. v002 adds `PPG::select_faces_by_normal` (with `tag_expression ""`, `invert true` and `set_face_tag "top_faces"`), then extrudes `top_faces`, and gives the predicted 10 faces and 12 vertices.

Lessons: predict outputs before verifying, and create PPG tags before selecting by them. Both are now in SKILL.md.

## Phase 5 test tasks (2026-10-29)

1. **Fix `cg_flat_layout_v001`** (Case E). Result: `work/cg_flat_layout/cg_flat_layout_v002.json` in the repo, VERIFIED. Installed with the user's go-ahead and reloaded live. A playblast showed the 2×2 block layout with ground, roads, junctions, sidewalks, lot guides and IDs; faint hatching at the outer road edges looked like viewport z-fighting and wasn't investigated further.
2. **Scatter graph from scratch.** Headless, then live (`claude_scatterShape`): 200 points, and the baked mesh had 1600 vertices and 1200 faces (8 and 6 per cube). A playblast confirmed the look. This needed the fan-in recipe for `create_instances.instance_geometries`. Two self-inflicted port-name errors were caught by node-index hints.
3. **PPG compound from scratch** (Case F). Result: `work/ppg_inset_block/ppg_inset_block_v002.json`, VERIFIED with the predicted counts.

## Evidence inventory and limits

- `assets/native-examples/manifest.json`: exact source digests, declared libraries and confirmation status.
- `ppg_nyc_skyscraper_v3_1_fast.json`: unmodified user-confirmed final graph; primary native building example.
- `cs_green_goo_v5(1).json`: unmodified working-format example supplied by the user.
- `ppg_nyc_skyscraper_bake_v3.json`: unmodified optional bake; no user confirmation of the baker itself.
- `ppg-docs/`: all 34 Markdown files extracted unchanged from the user's `docs.zip`.
- Original normalized Autodesk and PPG/VHH corpora: preserved with their original provenance.
- `native-endpoint-evidence.json`: observed port spellings in the three native examples, not full signatures or overload schemas.

Do not use the old v3 report's empty error list as runtime proof. Its scope check missed a real error. Keep static checks, numerical layout checks, user feedback and measured performance as distinct evidence classes. The new regression suite tests the export contract and scope defect without running Maya.
