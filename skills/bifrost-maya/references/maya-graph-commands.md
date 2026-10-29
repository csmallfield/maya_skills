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
- `bifrostGraph(importGraphAsShape=file)` fails with "Fail to load bifrost graph" for library compound files such as the skyscraper and goo exports. Those are compound definitions, not saved graphs.
- To test a new compound file without installing it into the user's folder, the next step is a temporary library config (`BIFROST_LIB_CONFIG_FILES`); that isn't built yet. Until then, don't write into the user's compounds folder without asking.

## Not yet verified

`bifrostGraph` flags `importGraph`, `serializeGraph`, `executionCounter` and `compilationCounter` (the counters may need a different call form), `vnnPort` fan-in flags, loops, terminals, and `bifcmd.exe`. `bifcmd.exe` fails to start here with a missing-DLL error (0xC0000135), even with Maya's `bin` on PATH.
