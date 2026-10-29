# Building Bifrost graphs with Maya commands

Verified on Maya 2026 with Bifrost 3.0.0.0 on 2026-10-29, both headless (`scripts/bifrost_headless.py`) and in the user's live Maya through `scripts/maya_exec.py`. The patterns come from Autodesk's own scripts in the install: `bifrost/python/site-packages/bifrost/maya/maya_compound_tester.py` and the USD pack's `bifrost_usd/graph_api.py` and `create_stage.py`.

## Contents
- Which tool to use
- Verified recipe
- Command reference
- What crashes Maya
- Reading results and errors
- Loading compound files
- Not yet verified

## Which tool to use

1. **`bifrost_headless.py`**: the default for trying anything new. It runs a separate `mayapy` process (about 35 s to start, so batch several specs per run). A crash there kills only that process.
2. **`maya_exec.py`**: the user's live Maya, for building what they will look at. Only use calls that already passed headless. Ask the user to save before editing their scene.

## Verified recipe

```python
g = cmds.createNode("bifrostGraphShape")              # or "bifrostBoard" for a board without a shape
node = cmds.vnnCompound(g, "/", addNode="BifrostGraph,Modeling::Primitive,create_mesh_cube")[0]
cmds.vnnNode(g, "/output", createInputPort=("mesh", "Object"))    # a graph OUTPUT is an input on /output
cmds.vnnConnect(g, f"/{node}.cube_mesh", ".mesh")                  # ".port" = graph boundary
cmds.vnnNode(g, f"/{node}", setPortDefaultValues=("width", "3"))   # values are strings in Bifrost literal form
cmds.bifrostGraph(g, createMayaGeometry="mesh")                    # makes a Maya mesh (meshShape) from the output
```

Result: one Maya mesh with 8 vertices and bounding box (-1.5, -0.5, -0.5) to (1.5, 0.5, 0.5).

## Command reference

| Task | Command |
|---|---|
| New graph | `cmds.createNode("bifrostGraphShape")` makes a shape under a transform; `"bifrostBoard"` makes a board |
| List nodes | `cmds.vnnCompound(g, "/", listNodes=True)`; a new graph has `input` and `output` |
| Add node | `cmds.vnnCompound(g, "/", addNode="BifrostGraph,<namespace>,<name>")` returns `[node_name]` |
| Add input or output node | `vnnCompound(g, "/", addIONode=True)` adds an input; `False` adds an output |
| Remove or rename | `vnnCompound(g, "/", removeNode=n)`, `vnnCompound(g, "/", renameNode=(old, new))` |
| New empty compound | `vnnCompound(g, "/", create="name")` |
| Graph output port | `vnnNode(g, "/output", createInputPort=(name, type))` |
| Graph input port | `vnnNode(g, "/input", createOutputPort=(name, type))` |
| Connect or disconnect | `vnnConnect(g, "/a.port", "/b.port")`; add `disconnect=True` to disconnect |
| Set or read a value | `vnnNode(g, "/n", setPortDefaultValues=(port, "text"))`; `queryPortDefaultValues=port` reads it back |
| Node ports and type | `vnnNode(g, "/n", listPorts=True)`, `vnnNode(g, "/n", queryTypeName=True)` |
| Port data type | `vnnCompound(g, "/", queryPortDataType="n.port")` |
| Batch edits | `vnnChangeBracket(g, open=True)` ... `vnnChangeBracket(g, close=True)` |
| Library browse | `cmds.vnn(libraries="BifrostGraph")`, `cmds.vnn(nodes=("BifrostGraph", lib))` |
| Output to Maya mesh | `bifrostGraph(g, createMayaGeometry=port)`, or by hand: `g.port` -> `bifrostGeoToMaya.bifrostGeo`, then `.mayaMesh[0]` -> `mesh.inMesh` |
| Export a compound | `vnnCompound(g, "/compound", publish=(file, namespace, "", False))`, `saveAs=file` |

Notes:
- Paths are scoped: `/` is the graph root, `/node` is a node in it, and `/compound/node` is inside a compound.
- Graph-boundary endpoints start with a dot (`.mesh`), matching Autodesk's `graph_api.connect`.
- Scalar output ports become readable Maya attributes: `cmds.getAttr(g + ".total_height")`. Object ports have attribute type `bifData` and can't be read with `getAttr`.
- `bifrostGraph` has no query mode; `q=True` raises "Invalid flag 'q'".

## Fan-in: connecting into an array port

`vnnConnect` can't target the parent of a fan-in port, so an `Object` going into `array<Object>` (for example `create_instances.instance_geometries`) fails with "Maya command error". Autodesk's `bifrost_usd/graph_api.py` (`connect_to_fanin_port`, BIFROST-9071) creates a child port and connects to that. Verified headless and live on 3.0:

```python
cmds.vnnChangeBracket(g, open=True)
cmds.vnnNode(g, "/instances", createInputPort=("instance_geometries.cube_mesh", "auto"))
cmds.vnnConnect(g, "/rock.cube_mesh", "/instances.instance_geometries.cube_mesh")
cmds.vnnChangeBracket(g, close=True)
```

Name the child after the source port, and add a number suffix if one exists (`vnnNode(g, "/n", listPortChildren=port)` lists them). In a `bifrost_headless.py` spec, write the target as `"instances.instance_geometries[]"`.

## Checking the look

Counts and bounds can't show whether something looks right. In live Maya, render one frame to a PNG and view it:

```python
cmds.setAttr("persp.translate", 22, 16, 22, type="double3"); cmds.setAttr("persp.rotate", -32, 45, 0, type="double3")
cmds.playblast(completeFilename="C:/tmp/look.png", format="image", compression="png", frame=[1],
               widthHeight=[960, 540], percent=100, viewer=False, showOrnaments=False, forceOverwrite=True, offScreen=True)
```

This moves the user's `persp` camera, so say so, or use a new camera. Bifrost instances display directly from the graph shape, with no conversion.

## What crashes Maya

- **`cmds.vnnNode(g, "/", createOutputPort=(...))`**: creating a port on the graph root crashes Maya outright. This crashed the user's session and was reproduced headless ("Fatal Error"). Graph ports always go on `/output` or `/input`.

When you find another crash, reproduce it headless, then add it here and to `tests/test_headless_harness.py` as a regression.

## Reading results and errors

- A failed `addNode` or `vnnConnect` raises a generic `RuntimeError: Maya command error`. The headless tool adds a hint from the node index, such as an unknown node or port.
- **Type errors don't raise.** They show up in Maya's output when the graph compiles:
  ```
  Error: while compiling top level compound 'bifrostGraphShape2', around the port 'bifrostGraphShape2.n':
  no promotion exists from a value of type 'Object' to a value of type 'long'
  ```
  Maya still evaluates and returns zero or default outputs, so a plausible-looking value is not proof the graph worked. `bifrost_headless.py` collects these lines for each graph and marks the graph as failed.
- In live Maya, compile errors go to the Script Editor rather than back to `maya_exec.py`. Test headless first.
- When the user's libraries load (VHH, MJCG and others), Maya prints a lot of warnings. The headless tool only reports what is printed while each graph is built and evaluated.

## Loading compound files

- Every JSON in the user's compounds folder (`~/Autodesk/Bifrost/Compounds`, library "UserCompounds") loads when the plugin loads, in headless sessions too. A compound there can be added by its full name. For example, `Procedural::Buildings::ppg_nyc_skyscraper_v3_1_fast` evaluates headless on 3.0 to `bay_count` 832 and `total_height` 166.9 in about 1.2 s.
- `bifrostGraph(importGraphAsShape=...)` takes a compound **name** that is already in a library, not a file path. It unpacks that compound into an editable graph, which is what Maya's Bifrost Browser does with examples. `importGraphAsShape="Graphs::Scatter::basic_scatter_example"` and `"FX::Goo::cs_green_goo_v5"` both work. A file path fails with "Fail to load bifrost graph", even for Autodesk's own example files.
- Compound files only register when the plugin loads. In a running session, a file added later stays invisible: `vnn(flushProxies="BifrostGraph")` doesn't help. Unloading and reloading the plugin does pick it up (verified headless with `file(new=True, force=True)`, `unloadPlugin("bifrostGraph", force=True)`, then `loadPlugin`). That avoids a full Maya restart but needs a new scene. Not yet tried in the live session.
- **Testing a file without installing it:** `bifrost_headless.py --library FILE` copies the file into a scratch library and points `BIFROST_LIB_CONFIG_FILES` at it for that run. A fresh mayapy loads it at startup, and the user's compounds folder is never touched. A scratch library config is just `{"AminoConfigurations": [{"vendorName": ..., "libraryName": ..., "libraryVersion": ..., "jsonLibs": [{"path": FOLDER}]}]}`.

## bifcmd.exe (command-line runner)

`bifrost/bin/bifcmd.exe` loads a definition JSON file **directly**, then compiles and optionally runs it, in about 10 s with no Maya. It needs two things:

- `bifrost/thirdparty/bin` on PATH. That's where `aic_1_2.dll` is; without it the exe exits with 0xC0000135.
- `BIFROST_DISABLE_PACKS=usd_pack`, unless the MayaUSD libraries are on PATH. Otherwise the USD pack fails to load and `configFilesLoadedOk` is false.

```
bifcmd.exe FILE.json [--compound-name NS::name] [--list-ports] [--set-port NAME VALUE] [--frames A B] --log-file LOG.json
```

The JSON log reports `compoundLoadedOk`, `compilationOk` and `executionOk` separately, with error and warning messages and an output summary (component counts, plus min, max and average of each property). Results:

- A test compound file that was never installed loaded, compiled and ran. `--set-port width 5` gave `point_position` from -2.5 to 2.5.
- The v3.1 skyscraper **compiled** with `--list-ports`, but bifcmd **crashed** (0xC0000005) when it executed. The same compound evaluates fine in mayapy.

- bifcmd **crashes** (0xC0000005, empty log) when the file redefines a compound that is already installed under the same name. A renamed copy compiles. `verify_compound.py` renames automatically. To check an installed compound, give no file, just `--compound-name`, and bifcmd compiles it from the libraries.
- With `--list-ports`, compile errors come back exactly as Maya reports them. For example, the old helper-scope bug gives *"Node 'tier_trim_records' has an unknown node definition 'nyc_affine_box_points'"*.

`scripts/bifcmd_check.py` wraps all of this. Use bifcmd as a fast load-and-compile check for compound files, and to run simple compounds. Use mayapy (`bifrost_headless.py`) to execute real graphs, and for anything needing Maya inputs or USD. bifcmd can't run compounds with overloads or `auto` ports.

## Not yet verified

`bifrostGraph` flags `importGraph` (by name it returned the name but added no nodes), `serializeGraph` (returns a binary int array), `executionCounter` and `compilationCounter`, `vnnPort` fan-in flags, loops, terminals, and reloading the plugin in the live session.


## Simulations headless

Verified 2026-10-29 on `Graphs::MPM::sand_pile`, `dust_motes` and `simple_RBD`. A graph with time-dependent nodes gets a `Simulation__time` attribute that Maya connects to `time1.outTime`, headless too. Stepping `cmds.currentTime` alone isn't enough:

- **Turn off async evaluation:** `cmds.bifrostGraph(g, enableAsync=False)`.
- **Pull outputs on every frame, in order.** Read every output (`getAttr`, mesh queries) at every frame, not just the frames you report.

If you skip either, every sampled frame returns the frame-1 state, and each frame "takes" about 1 ms. A per-frame time of milliseconds for a real sim is a sign that nothing is being computed.

## USD pack outside Maya

bifcmd only loads `packs/usd_pack/<ver>` when these are on PATH: MayaUSD's `C:/Program Files/Autodesk/MayaUSD/Maya2026/<mayausd>/mayausd/USD_<ver>/lib` and `.../bin`, and `C:/Program Files/Autodesk/Maya2026/bin`. Also set `PXR_PLUGINPATH_NAME` to `.../USD_<ver>/lib/usd`. Without these, the pack fails with "Default value function not found for value of type 'BifrostUsd::Stage'" and `configFilesLoadedOk` is false. `bifcmd_check.usd_environment()` finds them. Headless mayapy needs none of this.
