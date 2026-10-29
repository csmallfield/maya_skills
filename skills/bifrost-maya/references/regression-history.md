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

## Evidence inventory and limits

- `assets/native-examples/manifest.json`: exact source digests, declared libraries and confirmation status.
- `ppg_nyc_skyscraper_v3_1_fast.json`: unmodified user-confirmed final graph; primary native building example.
- `cs_green_goo_v5(1).json`: unmodified working-format example supplied by the user.
- `ppg_nyc_skyscraper_bake_v3.json`: unmodified optional bake; no user confirmation of the baker itself.
- `ppg-docs/`: all 34 Markdown files extracted unchanged from the user's `docs.zip`.
- Original normalized Autodesk and PPG/VHH corpora: preserved with their original provenance.
- `native-endpoint-evidence.json`: observed port spellings in the three native examples, not full signatures or overload schemas.

Do not use the old v3 report's empty error list as runtime proof. Its scope check missed a real error. Keep static checks, numerical layout checks, user feedback and measured performance as distinct evidence classes. The new regression suite tests the export contract and scope defect without running Maya.
