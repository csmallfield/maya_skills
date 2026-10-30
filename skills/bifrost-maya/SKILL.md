---
name: bifrost-maya
description: Design, build, inspect, debug and optimize Autodesk Bifrost graphs in Maya (Bifrost 3.0 on Maya 2026). Use for any Bifrost work - exact node names, ports and defaults; Maya-loadable native compound JSON; registration, scope or type errors; PPG procedural buildings and polygon modeling; VHH tools; scattering and instancing; fields and volumes; particles, Aero, liquids, MPM, rigid bodies, oceans; rigging; diagnostics and rendering; or driving a live Maya session through its Python command port.
---

# Bifrost for Maya

Work like a senior procedural TD: reason from data types and graph architecture, take exact node facts from the installed library index, and use Autodesk example graphs as evidence for idiomatic construction.

Paths below are relative to this skill's folder. Run scripts with `python -I scripts/<name>.py`.

## Evidence order

Use the strongest source available for each claim, and say which one you used.

1. **Installed library index** (`references/bifrost-3.0.0.0/`) - generated from the shipped Bifrost 3.0 library JSON. Authoritative for node names, port names, port types, defaults, overload counts, enums and renames. Query it with `scripts/node_info.py`.
2. **User-confirmed native exports** (`assets/native-examples/`, see `manifest.json`) - authoritative for serialization conventions: envelope, typed literals, loops, dynamic ports, scope.
3. **Autodesk example graphs** (`references/workflow-data/`) - idiomatic patterns. These are identical to the 105 graphs shipped with 3.0.
4. **User-supplied compound corpus** (`references/compound-data/`: PPG 2.80 beta1 as installed, VHH and others) and the 34 PPG docs (`references/ppg-docs/`) - exact interfaces for those libraries. For a graph written against PPG 2.0, check `references/ppg-2.0-vs-2.80.md`.
5. **Condensed node summaries** (`references/nodes-*.md`) - discovery and search terms only. Never quote their port names as exact; one of them had the cube's ports wrong.
6. **Inference** - label it as a design recommendation.

Don't invent node names, ports, enum values, property names or signatures. If no source supports a detail, look it up with `node_info.py` or in Maya. If you still can't confirm it, say that it needs checking.

## Node lookup

```
python -I scripts/node_info.py create_mesh_cube              # ports, types, defaults, summary
python -I scripts/node_info.py --search "scatter on surface"  # ranked search
python -I scripts/node_info.py scatter_points --doc           # shipped Autodesk doc
python -I scripts/node_info.py Core::Math::add --overloads    # every exact signature
python -I scripts/node_info.py --type ScatteringMode          # enum members
python -I scripts/node_info.py --renamed <old::name>          # 2.x -> 3.0 renames
```

- `builtin` entries (`Core::Logic::if`, array built-ins, `Core::Graph::terminal`, ...) have no library signature. Their ports are the spellings seen in shipped graphs, and their types resolve from connections.
- Internal nodes are hidden unless you pass `--internal`. Don't build user graphs on internal nodes unless an Autodesk compound does the same.
- `--doc` and `--overloads` read from the install (`BIFROST_ROOT` overrides the recorded path). For a new Bifrost version, run `python -I scripts/build_node_index.py "<install>/<version>/bifrost"`. This writes a new `references/bifrost-<version>/` folder, and `node_info.py` picks the newest one.

Version facts from the 3.0 install: operators declare `Amino 3.0.0.0`, while shipped compounds still declare `2.15.0.9` for their libraries. So a `2.15.0.9` dependency in an export is not by itself a version error. All node types used by the bundled skyscraper v3.1 and goo examples resolve in 3.0.

## Core workflow

1. Classify the task by domain and by the output data type it needs.
2. Read `references/concepts.md` when architecture, debugging, simulation, transforms, fields or properties matter.
3. Find candidate nodes with `node_info.py --search`, browsing `references/nodes-*.md` for vocabulary. Run `node_info.py <name>` on every node you'll use **before** you write a spec or a file, and copy the port names and types from its output, not from memory. Most self-inflicted errors in testing were remembered port names (`point_count` for `count`, `mesh` for `merged_meshes`) and type spellings (`unsigned int` for `uint`).
4. If the request mentions PPG, VHH or another supplied compound, read `references/compound-concepts.md`. Then run `scripts/search_compounds.py` and `scripts/inspect_compound.py` on the best match.
5. Before inventing a complex built-in pattern, search Autodesk examples with `scripts/search_graph_examples.py "<intent, nodes, concepts>"`. Inspect one to three close matches with `scripts/inspect_graph.py <graph_id>`. Ranking weights the graph's name, then its category and description, then its node types, with its documentation counting least. Browse `references/workflow-index.md` by category when a query is vague.
6. Design hierarchically: main dataflow first, then key compounds, properties and fields, controls, diagnostics, caching and output. For PPG buildings or repeated detail, read `references/ppg-building-design.md` first.
7. Deliver the artifact that was asked for. For a Maya-loadable compound, read `references/native-json.md` and follow the native gate below.
8. In live Maya, build in stages and inspect as you go (see Maya execution). Otherwise, keep offline checks separate from runtime results.

## Retrieval discipline

- Don't load whole corpora into context. Use the scripts and inspect only the relevant scope of a large graph.
- `references/workflow-patterns.md` is a frequency hint, not a recommendation.
- `references/compound-data/ppg-overview.md` and `vhh-overview.md` let you browse those families. `interface-index.json` gives exact custom signatures, and `type-definitions.json` gives custom enums.
- `references/compound-data/unresolved-dependencies.json` lists custom-corpus references that aren't defined anywhere: MJCG, Hyuu and Deep_Learning nodes, which need their own libraries.
- `references/installed-compounds-3.0.md` says which of the user's installed compounds compile on 3.0. `cg_flat_layout_v001` has real type errors.
- `references/node-gotchas.md` lists node type-inference traps and proven vectorised idioms (closest-point cutoff tests, boolean cutters from instances, strand segment pairs).
- `references/source-notes.md` covers provenance. `references/regression-history.md` covers the native-format, layout, performance and helper-scope lessons.

## Reasoning rules

- Say which kind of claim you're making: **installed-library fact**, **Autodesk example evidence**, **user-supplied compound evidence**, **user-reported result**, or **inference**.
- Prefer fully qualified node types when names could be ambiguous, for example `Modeling::Points::scatter_points`.
- Pitch the answer at the user's level. For an experienced TD, focus on topology, properties, type flow, performance and failure modes, not UI clicks.
- Examples are patterns, not templates. Adapt values to scale, units, resolution and intent.
- User feedback is user-reported evidence. Don't turn static node counts or layout checks into runtime benchmarks.

## Existing graph analysis

1. Identify inputs and outputs, terminal states, major compounds and data types.
2. Trace the main output backward to find the critical dataflow spine.
3. Find where properties are created and used, plus fields, stateful simulation, caches and type conversions.
4. Check unusual nodes with `node_info.py` (including `--renamed` for 2.x files) and against the nearest Autodesk examples.
5. Report concrete issues: type mismatch, missing property, wrong component domain, transform semantics, unresolved fan-in, renamed or missing node, or a disconnected output.
6. Before changing anything, classify the failure: registration or file format, local type resolution, compile or type flow, output visibility, geometry or layout, or performance. Keep correctness fixes separate from optimization.

## New graph design

Use this structure when it helps: **Intent and output**, **Inputs**, **Main dataflow**, **Key properties** (names, domains, types), **Controls** (with ranges), **Diagnostics**, **Performance** (resolution, accelerators, instancing, caching), and **Version notes**. When implementation detail is asked for, expand the dataflow into exact node instances and `source.port -> target.port` connections, with each port checked in `node_info.py`.

**Expose few input ports.** Make a value a compound input only if an artist will realistically change it per use: the handful of controls that define the result, such as size, count, seed or style, and the input geometry. Everything else stays inside as a value or value node: unit conversions, epsilons, tag names, debug and display toggles, internal ratios, and settings with one sensible answer. Users can still dig in and edit an internal value; a wall of ports buries the few that matter. For reference, Autodesk's 105 example graphs expose a median of 0 inputs (103 of them expose 3 or fewer), while the Astra-era files expose 15 (`cg_flat_layout_v001`), 21 (skyscraper v3.1) and 56 (`ppg_urban_multistyle_v4_3`). Astra tended to promote every option to a port; don't. When a design needs more than about 6 to 8 inputs, list which ones are truly per-use, and keep the rest internal or group them behind one preset or style input. When the user asks to fix or extend an existing file, keep its public interface unless they ask to trim it, and suggest the trim separately.

## Native JSON and scope gate

A request for a compound JSON to load in Maya means native Bifrost serialization, not a blueprint. Follow `references/native-json.md`. Use the user-confirmed v3.1 example for layout, loop, dynamic-input and literal conventions.

**Never put a literal on a multi-input child port** (`add.first.in_1`, `multiply.first.b`). Bifrost drops it and treats the child as 0, and it still compiles, so `x × 2` silently becomes 0. Feed constants into multi-input ports from a wired value node, and do the same for a constant array meant to auto-loop through a scalar operator. The v3.1 example itself has one such defect (`regression-history.md`, Case E), so don't copy its literal placement onto multi-input ports.

Before delivery, run `python -I scripts/verify_compound.py FILE [--set PORT=VALUE]` and fix everything it reports. It runs three stages and gives one verdict:

1. **static**: `validate_native_graph.py --strict-evidence`, which checks format, local scope and exact 3.0 ports on shipped nodes. Every private helper must resolve in the scope that calls it, not just somewhere in the file.
2. **compile**: `bifcmd` loads and compiles the file directly, in about 10 s.
3. **evaluate**: a headless Maya loads the file from a scratch library, unpacks the compound and reads its outputs, in about 40 s.

Before running verify, write down what the outputs should be, such as face and vertex counts, bounds or derived values. Then compare: a VERIFIED file whose outputs don't match the prediction is wrong (in testing, an extrude that selected nothing still verified, with an unchanged 6-face cube). Claim a file works only when the verdict is VERIFIED and the outputs match. Then say what was read (scalar values; mesh, vertex and face counts with bounds; for `array<Object>` outputs, the element count and the merged mesh) and what wasn't (custom types, the look). Check the numbers against the inputs: a plausible-looking value isn't proof. `--fast` skips evaluate and gives PARTIAL. If the compound is already installed under the same name, the script checks a renamed temporary copy, because a duplicate name crashes `bifcmd`. When the validator or bundled examples change, run `python -I -m unittest discover -s tests -v`.

Deliver the actual file, its exact registered name, dependencies, the verify verdict with its outputs, and any untested behavior. For a scope or registration fix, use a fresh versioned name rather than assuming an existing scene node picks up the replaced file. Installing a file means copying it into the user's compounds folder, and Maya only sees it after the Bifrost plugin reloads or Maya restarts. Ask before writing there. Once the user says to install, use `scripts/install_compound.py FILE --yes [--reload]` (add `--compound NS::name` for a library file holding several compounds). It verifies first and refuses anything not VERIFIED, and it backs up a different file of the same name instead of overwriting it, as `<name>.json.bak-<time>` (Bifrost loads every `.json` in the folder, so a backup ending in `.json` shadowed the new install). Never edit a compound after installing it without reinstalling: an installed copy that differs from the repo is what other compounds resolve against. `--reload` reloads the Bifrost plugin in live Maya, but only when the scene has no unsaved changes (it needs a new scene); a saved scene is reopened afterwards.

## PPG performance gate

Read `references/ppg-building-design.md`. Keep shared PPG prototype topology separate from lightweight tier and elevation placement and from retained native instancing. Use supported quad-relative cuts, deliberate tags and edge orientation, and explicit counts and repeat modes. Keep material splits, welds and normal work off the full-building path wherever prototype processing is enough.

**PPG selects faces by its own face tags**, not Bifrost component tags. `PPG_extrude` with `tag_expression "face_top_tag"` on a `create_mesh_cube` selects nothing and silently passes the mesh through. Create PPG tags first: use `PPG::select_faces_by_normal` (with `tag_expression ""` and `invert true` to consider every face, and `set_face_tag` naming the result), or `set_face_tag` / `set_face_ID_tags`. Then select by that tag. `tag_expression ""` plus `invert true` selects all faces, which is the pattern the v3.1 skyscraper uses.

Don't assume `PPG_instance` keeps native instances; check its supplied implementation. Say whether modules stretch with the prototype or keep absolute detail sizes. Measure warm evaluation separately from compile, display and bake.

## Maya execution

Read `references/maya-graph-commands.md` before building graphs with commands. It has the verified recipe, the command reference, the known crash, and how errors show up.

**Test headless first.** (A spec can't wire multi-input math such as `add`; use native JSON for those, see `maya-graph-commands.md`.) `scripts/bifrost_headless.py SPEC [--library FILE]` builds and evaluates graphs from a JSON spec in a separate `mayapy` process. `--library` loads a compound file that isn't installed, and `"graph": "NS::name"` unpacks a library compound into an editable graph. A crash there can't touch the user's session. It reports each step, outputs (scalar values, or mesh, vertex and face counts with bounds), compile errors and timing. Runs go to a persistent background `mayapy` worker: the first run starts it (about 35 s) and later runs take 1 to 2 s, so iterate freely. It exits after 30 idle minutes, or with `--stop-worker`. If it crashes, the run reports that and the next run starts a fresh one. Every Object output also gets an automatic `<port>__points` count, so points, volumes and instances get numbers too.

**Simulations:** add `"frames": [start, end]` and `"sample_frames"` to a spec, or pass `verify_compound.py --frames START END`. Every frame is computed in order with async evaluation off, and outputs are read at the sample frames. Check that the numbers change between frames. Before this was handled correctly, a sim returned frame 1 at every sample, with plausible values. Proven on `Graphs::MPM::sand_pile`: the column fell from 8.07 to 1.98 units tall and spread from ±4 to ±9 over 24 frames, at about 2.9 s per frame. To measure motion, wire `Geometry::Points::get_bounding_box.aabb_mesh` to an Object output and compare its bounds across frames.

**USD:** `bifcmd_check.py`, `verify_compound.py` and `scan_compounds.py` load the USD pack automatically, using MayaUSD's matching `USD_<ver>` libraries plus Maya's `bin` folder. Headless Maya loads USD on its own. Nothing extra needs downloading. Installed user compounds (`~/Autodesk/Bifrost/Compounds`) are available there too.

**Then use live Maya.** The user's Maya opens a Python command port on `localhost:7001`. `scripts/maya_exec.py -c CODE` (or a file, or `-` for stdin) runs code there with `cmds` and `mel` already imported. It returns the last expression's value, printed output and any traceback as JSON.

- Only send live calls that already passed headless. Ask the user to save before editing their scene. `vnnNode(g, "/", createOutputPort=...)` crashes Maya: graph ports go on `/output` (`createInputPort`) or `/input` (`createOutputPort`).
- Type errors don't raise. Bifrost prints them when the graph compiles and still returns default outputs. Trust a result only after a headless run reports no compile errors.
- Check the Bifrost version (`cmds.pluginInfo('bifrostGraph', q=True, version=True)`) when node availability matters.
- Build a minimal graph that produces inspectable output, then add one logical block at a time and check after each major block.
- Keep node names meaningful and compound boundaries intact. Don't make scene changes the request didn't ask for, and don't write into the user's compounds folder without asking.
- An `Object` can't connect directly into an `array<Object>` port (for example `create_instances.instance_geometries`). It needs a fan-in child: in a spec, target `node.port[]`; live, see the fan-in recipe in `references/maya-graph-commands.md`.
- To check the look, playblast one frame to a PNG and view the image (recipe in `references/maya-graph-commands.md`). Counts and bounds don't show whether something looks right.
- Report what you created and tested (headless or live) separately from what is still a proposal.

## Scripts

- `node_info.py` - exact node lookup against the installed-library index (see above).
- `verify_compound.py FILE [--compound NAME] [--set PORT=VALUE] [--frames A B] [--fast]` - static, compile and evaluate checks with one verdict.
- `bifcmd_check.py [FILE] [--compound-name NAME] [--run]` - compile (or run) a compound file, or an installed compound by name, with bifcmd.
- `scan_compounds.py [FOLDER] [--out REPORT.md]` - compile-check every installed compound in a folder.
- `bifrost_headless.py SPEC [--library FILE] [--json] [--no-worker] [--stop-worker]` - build and evaluate graph specs (including frame ranges) in a separate headless Maya.
- `install_compound.py FILE --yes [--reload] [--compound NAME]` - verify, install into the user's compounds folder with a backup, and optionally reload Bifrost live.
- `maya_exec.py [-c CODE | FILE | -] [--port N] [--persist]` - run Python in the user's live Maya through its command port.
- `build_node_index.py BIFROST_ROOT [--out DIR]` - rebuild that index from an install.
- `search_graph_examples.py QUERY [--limit N]` / `inspect_graph.py GRAPH_ID [--connections N]` - Autodesk example graphs.
- `search_compounds.py QUERY [--limit N] [--collection NAME]` / `inspect_compound.py COMPOUND_OR_ID` - custom compound corpus.
- `inspect_native_graph.py FILE [--tree] [--path PATH]` - one native compound scope, including loop flags and dynamic ports.
- `validate_native_graph.py FILE [--strict-evidence] [--json-report PATH]` - offline native-file preflight.
- `parse_graphs.py` / `parse_compounds.py SOURCE_DIR OUT_DIR` - rebuild the normalized corpora.
- `python -I -m unittest discover -s tests -v` - regression suite. Set `BIFROST_HEADLESS_TESTS=1` to also run the mayapy test, which takes about 45 s.
