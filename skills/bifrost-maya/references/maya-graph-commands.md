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

This moves the user's `persp` camera, so say so, or use a new camera. For large scenes, set the camera shape's `nearClipPlane` to 1 or even 10 (`cmds.setAttr(shape + ".nearClipPlane", 1)`). Maya's default 0.1 with a far clip in the thousands produces black hatching and z-fighting on coplanar or near-coplanar faces. It's a depth-precision problem, so don't move the geometry to fix it (user tip, confirmed on the CityGen city in 2026-10). Bifrost instances display directly from the graph shape, with no conversion.

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
- Compound files only register when the plugin loads. In a running session, a file added later stays invisible: `vnn(flushProxies="BifrostGraph")` doesn't help. Unloading and reloading the plugin does pick it up (verified headless with `file(new=True, force=True)`, `unloadPlugin("bifrostGraph", force=True)`, then `loadPlugin`). That avoids a full Maya restart but needs a new scene. Verified live on 2026-10-29: `install_compound.py --yes --reload` installed `cg_flat_layout_v002` and reloaded Bifrost in the user's Maya (about 1 minute including verification). The compound was available straight away, and `importGraphAsShape` by name built it.
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

`bifrostGraph` flags `importGraph` (by name it returned the name but added no nodes), `serializeGraph` (returns a binary int array), `executionCounter` and `compilationCounter`, `vnnPort` fan-in flags, loops and terminals.


## Simulations headless

Verified 2026-10-29 on `Graphs::MPM::sand_pile`, `dust_motes` and `simple_RBD`. A graph with time-dependent nodes gets a `Simulation__time` attribute that Maya connects to `time1.outTime`, headless too. Stepping `cmds.currentTime` alone isn't enough:

- **Turn off async evaluation:** `cmds.bifrostGraph(g, enableAsync=False)`.
- **Pull outputs on every frame, in order.** Read every output (`getAttr`, mesh queries) at every frame, not just the frames you report.

If you skip either, every sampled frame returns the frame-1 state, and each frame "takes" about 1 ms. A per-frame time of milliseconds for a real sim is a sign that nothing is being computed.

## USD pack outside Maya

bifcmd only loads `packs/usd_pack/<ver>` when these are on PATH: MayaUSD's `C:/Program Files/Autodesk/MayaUSD/Maya2026/<mayausd>/mayausd/USD_<ver>/lib` and `.../bin`, and `C:/Program Files/Autodesk/Maya2026/bin`. Also set `PXR_PLUGINPATH_NAME` to `.../USD_<ver>/lib/usd`. Without these, the pack fails with "Default value function not found for value of type 'BifrostUsd::Stage'" and `configFilesLoadedOk` is false. `bifcmd_check.usd_environment()` finds them. Headless mayapy needs none of this.

## Setting a compound's inputs in a headless spec

`"graph": "NS::compound"` unpacks the compound, and its inputs become graph-boundary ports with no node path: `"values": {"size": "2000"}` fails with "The node path /size was not found", and the graph still evaluates with the defaults (seen 2026-10-30, CityGen v017). To run a compound with other input values, place it as a node instead: `"nodes": [{"type": "NS::compound", "name": "city"}]`, set `"city.size"`, and wire the outputs you read (`["city.lot_count", ".lot_count"]`). Read only scalar outputs when timing: Object outputs are converted to Maya geometry, which adds time. Put the same spec twice in the list to get a warm second run.

## Multi-input math in headless specs

`vnnConnect` can't wire the operands of multi-input operators (`Core::Math::add`, `subtract`, `multiply`, `divide`, `max`, `Core::Array::build_array`) in a fresh graph: `add.first` fails with "A port named first was not found", and `add.first[]` fails the same way. The node then compiles with "the multi-in node add has no input port". So a `bifrost_headless.py` spec can't build math chains yet (seen 2026-10-29). Write those graphs as native compound JSON instead (`first.in_0`, `first.in_1` listed in `multiInPortNames`; subtract and divide take the first child minus or divided by the rest), and test them with `verify_compound.py`, or with `--library FILE` plus a spec that places the compound as a node.

## USD point instancer from Bifrost instances

Verified 2026-10-29 (CityGen slice, `.usda` written by `export_stage_to_file`): feed a `create_instances` result straight into `USD::Prim::define_usd_point_instancer.points` and leave `prototype_definitions` empty. Its implementation sees `point_instance_id` and builds the prototypes from the instance shapes itself: `<instancer>/prototypes/obj_N` scopes, each with `_render` and `_proxy` meshes, plus a default material. `protoIndices`, `positions`, `orientations` (from `point_orientation`) and `scales` (from `point_scale`) are filled in, so no per-prototype `define_usd_mesh` loop is needed. Gaps: the stage has no `metersPerUnit` or `upAxis` metadata, and `/City`-style parent prims are created as typeless `def`s. Mesh prims passed to the same `add_to_stage` fan-in can use full paths such as `/City/Ground`.

`mayapy -I` can't import `pxr` (MayaUSD adds it through the environment that `-I` ignores). Read a `.usda` as text, or run mayapy without `-I` for pxr checks.

## Library files with several compounds

A file that holds a whole pipeline (several top-level compounds, one chaining the others) installs as one file: `install_compound.py FILE --compound NS::top --yes --reload`. `verify_compound.py` renames **every** top-level compound in the file that is already installed (and rewrites calls to them), so re-verifying after install works. Before that fix, the siblings failed compile with "overloaded operator ... has the same input ports signature as a previously defined operator".

## USD layers in live Maya: what not to do from the command port (2026-10-29)

- `Sdf.Layer.Find(path).Reload()` on a layer that a mayaUsdProxyShape's stage composes raises "Detected usd threading violation. Concurrent changes to layer(s) composed in stage ...".
- Wrapping that in `maya.utils.executeInMainThreadWithResult` **hung Maya**: the process stayed alive but the command port stopped answering. Command-port code already runs on the main thread, so the call waits on itself.
- **A Bifrost USD write fails silently onto a path still loaded in the session's layer registry** (seen 2026-10-30): after a previous write and a `layer.Reload()` of that file, the graph's written flag came back false and the file was unchanged, even in a new scene. Writing to a new file name worked; with no proxy shape using the old file, moving the new file over it on disk is safe. Check the written flag, not just the file's existence.
- Deleting and recreating the proxy shape does **not** pick up changed asset files: the referenced layers stay loaded in the session's layer registry (`Sdf.Layer.GetLoadedLayers()` still lists them). Changed assets show after a new scene/Maya start. Ask the user before anything that could block their session.

## Reading Maya geometry into a graph by path (verified live 2026-10-29)

Autodesk's USD pack (`bifrost_usd/author_usd_graph.py`, `_add_maya_mesh_to_stage`) reads Maya meshes into a graph through an IO node with a path option. From a script:

```python
io = cmds.vnnCompound(g, "/", addIONode=True)[0]          # a new input node, e.g. "input1"
cmds.vnnNode(g, "/" + io, createOutputPort=("basis_mesh", "Object"),
             portOptions="pathinfo={path=|grp|meshTransform|meshShape;setOperation=+;active=true}")
port = cmds.vnnNode(g, "/" + io, listPorts=True)[0]       # "input1.basis_mesh"
cmds.vnnConnect(g, "/" + port, "/some_node.mesh")
```

- Give the **mesh shape** path. It arrives in world space and updates live when the mesh is edited. A transform or group path gives an empty Object, and wildcards give 0 points.
- One path per port. `pathinfo={...}{...}` and `pathinfo={...},{...}` raise "Invalid port options".
- Port names are unique across **all** input nodes: a second `m` becomes `m1`, so read the real name back with `listPorts`.
- `bifrostGraph(g, inputByPathSuggestedTypes=path)` returned an empty list for locators and meshes alike, so don't rely on it.
- **What a mesh brings** (probed 2026-10-30 with `Core::Object::get_property_keys`): `point_position`, `face_offset`, `face_vertex`, `face_vertex_normal` (+ `_index`), `point_normal`, `face_vertex_uv` (+ `_index`), the component objects, `render_settings`, and **one property per colour set, named after the set**: `array<Math::float4>` targeting `point_component`, with (-1, -1, -1, -1) on unpainted points. So a colour set is a paintable per-point (or, read at a face's first corner, per-face) control; read it with `get_geo_property` typed `array<Math::float4>`, and treat an empty array (no such set) and -1 as unset. Verified by painting: CityGen v034 reads element decay from a set's red channel.
- In one probe, a pathinfo port on the `input` node that `addIONode` returned in a **fresh** graph read an empty Object, while the same port on `input1` (a graph that already had `input`) worked. If a by-path port reads empty, add the probe nodes to a graph whose by-path input already works.
- Probing live: `vnnNode(..., setPortDataType=("type", "array<Math::float4>"))` types an `auto` port such as `get_geo_property.type`. `getAttr` on an `array<string>` graph output returned `[[]]`; read `array_size` and then each element through `get_from_array` into a `string` output.
- Shipped graphs (`generate_data_example.ma`) store locator inputs as `array<Math::float4x4>` ports with space-separated `/`-style paths. Recreating that from a script returned no matrices; unresolved.

- **A graph writing the file a proxy shape shows can crash Maya** (2026-10-31, CityGen v037): a bifrostGraphShape
  with `usd_file` set and its `usd_written` output exposed wrote `city_live.usda`; creating a `mayaUsdProxyShape` on
  that file and then hiding the graph (which re-evaluates it) killed Maya within the same command. Bifrost's USD
  export and MayaUSD share the in-process layer registry. View a copy of the file, or clear `usd_file` before
  opening it in a proxy. Also: a graph output port that nothing pulls is never computed, so a `usd_file` set on a
  graph whose `usd_written` isn't exposed (and read) writes nothing.

- **pxr without live Maya** (verified 2026-10-31, CityGen asset scan): headless `mayapy` with `maya.standalone.initialize()` and `cmds.loadPlugin("mayaUsdPlugin")` imports `pxr` (USD 0.24.11 in Maya 2026), so USD scans and checks need no command port. A Bifrost graph shape built in headless mayapy also reads Maya meshes and colour sets by path (`pathinfo` ports), and `polyColorPerVertex(..., rgb=..., a=1)` paints vertices that Bifrost then reads, so a scene setup script can be tested end to end there.
