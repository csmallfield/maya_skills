# Native Bifrost JSON: delivery and validation

## Contents
- Output contract and evidence order
- Export structure and typed values
- Private compound scope
- Loops and dynamic ports
- Validation and delivery

## Output contract and evidence order

Treat a request for a compound JSON to load into Maya as a request for **native Bifrost compound serialization**, not a graph blueprint. A valid JSON document describing nodes is not necessarily a Bifrost file. Do not rename a design specification `.json` and present it as loadable.

Use the following evidence order for exact implementation:
1. A native export that the user confirms works in the target environment.
2. Actual exported Autodesk/custom compound definitions, including version declarations, public signatures and literal values.
3. Normalized corpus records for topology, interfaces and discovery.
4. Compact node-reference summaries for intent and search terms, not serialization authority.

Do not reconstruct native serialization solely from normalized records: normalization can omit UI metadata, loop flags, dynamic-port declarations or other native fields. Read the actual export for those fields. Do not silently reconcile conflicting sources. Preserve their versions and explain which source governs the implementation.

Use `assets/native-examples/ppg_nyc_skyscraper_v3_1_fast.json` as the user-confirmed PPG/native-instance reference, and `cs_green_goo_v5(1).json` as the earlier working export. Read the manifest before treating an example as runtime-confirmed. These are project examples, not universal schemas for all Bifrost versions.

Generate native JSON outside Maya when the required serialization evidence is available. State that offline generation is not Maya compilation. When native evidence is missing, obtain a working export or explicitly agree on a blueprint instead of silently substituting one.

## Export structure and typed values

Preserve the observed envelope:

```json
{
  "header": {"metadata": [{"metaName": "adskFileFormatVersion", "metaValue": "100L"}]},
  "namespaces": [],
  "types": [],
  "compounds": []
}
```

Populate `compounds` with real definitions. Use each definition's `name`, `ports`, `compounds`, `compoundNodes`, `connections`, `values`, `metadata`, `reservedNodeNames`, `terminalStates` where present, and `libraryDependencies`. Keep definitions in `compounds` separate from their instances in `compoundNodes`. The envelope above is illustrative and intentionally empty; do not deliver it as a functioning compound.

Follow the working example for:
- `portName`, `portDirection`, `portType`, and optional `portDefault`.
- `nodeName` plus `nodeType`, or a native value node's `valueType`.
- `source` / `target` endpoints, with `.port_name` denoting the enclosing interface.
- `valueName`, `valueType`, and typed `value` payloads.
- I/O layout metadata listing the real public ports; readable internal names and positions.
- Matching library declarations. `2.15.0.9` is the declaration in these working files, not a claim about every installed Maya component or the latest release.

Preserve typed literal conventions from the target export: `"1f"` for float, `"1L"` for int, `"1U"` for uint, `"0"` for long, `"true"`/`"false"` for bool, and `Math::float3` payloads with `x`, `y`, `z`. Do not blindly convert these to generic JSON numbers/booleans. Preserve case-sensitive port and enum spelling. Treat unspecified/auto ports as unspecified until topology or runtime resolves them.

For the observed primitive correction, use `Modeling::Primitive::create_mesh_cube.width`, `.length`, `.height`, `.position`, `.up_axis`, `.base_to_pivot`, and output `.cube_mesh`. Do not generate the former summary's guessed `size`, `divisions`, or `mesh` interface. For planes in this example, use `width`, `length`, `width_segments`, `length_segments`, and `plane_mesh`. These are observed interfaces, not exhaustive signatures.

## Private compound scope

Classify every node type as an external registered compound, an internal local definition, or a native value node. An authored name such as `nyc_affine_box_points` is legitimate **only when its implementation is included and resolvable**; it is not an Autodesk/PPG dependency to ask the user to install.

For this native-export pattern, place unqualified private helper definitions directly in the calling compound's own `compounds` array. Do not assume a helper defined in a parent or another branch is visible to a nested loop. A whole-file set of type names is not a scope validator.

The v3 failure and v3.1 repair are:

```text
nyc_instance_layout
  compounds:
    nyc_affine_box_points       # for crown and entrance calls here
    nyc_for_each_tier
      compounds:
        nyc_for_each_elevation
        nyc_affine_box_points   # required local copy for tier_trim_records
      compoundNodes:
        tier_trim_records : nyc_affine_box_points
```

Keep the two definitions identical when reusing this helper. Alternatively publish a deliberately namespaced external dependency, but only when its installation and interface are established. Do not invent a registered namespace as a shortcut.

Distinguish **stored definitions** from **calls/evaluated work**. The v3.1 scope repair adds an 11-node definition copy but no additional helper call. A larger serialized file can fix resolution without undoing the intended performance architecture. Treat immediate-scope checking as a conservative authoring profile supported by this case, not a complete statement of all Bifrost name-resolution possibilities.

## Loops and dynamic ports

Copy `forEachCompound` and `portIterationTarget` patterns from a native loop export, not a pseudo-node named `for_each`. In the working example, iteration-target ports are serialized as arrays outside the loop and consumed/produced as individual elements inside it; shared controls are not iteration targets. Preserve those flags and distinguish the outside type from the inside type. Inspect broadcasting and corresponding array lengths separately at runtime.

Preserve `fanInPortNames` and `multiInPortNames` on node instances. A fan-in endpoint such as `instance_geometries.prototype` needs its `prototype` child declared under that fan-in. A dynamic math endpoint such as `first.output1` needs `output1` in `multiInPortNames`. Do not replace observed child paths with guessed flat port names.

## Validation and delivery

Run the bundled preflight:

```bash
python scripts/validate_native_graph.py path/to/compound.json --strict-evidence --json-report validation.json
python -m unittest discover -s tests -v
```

Use `scripts/inspect_native_graph.py FILE --path root/nyc_instance_layout/nyc_for_each_tier` for a targeted native read. Use `--tree` to discover paths.

The validator checks the generated-file profile: envelope, names, immediate local scope, interface endpoints/directions, observed external endpoint spellings, declared dynamic children, duplicate targets/values, undriven outputs and local dataflow cycles. It deliberately does **not** compile Amino, infer overloads, evaluate fields/PPG, verify all value types, prove renderer compatibility or measure performance. Evidence coverage is separate from structural errors. Overloaded local definitions and unfamiliar native constructs require source/runtime review rather than treating the validator as a universal schema.

Require a negative regression: remove the tier-local helper from a copy of v3.1 and confirm `UNRESOLVED_LOCAL_TYPE`; feed a graph blueprint and confirm `NOT_NATIVE_COMPOUND`. Do not weaken the checker just to obtain a green report. Investigate warnings and consult the target library for unknown external endpoints.

Record separately: JSON parse, structural preflight, source/interface evidence, independent numeric checks, user-reported Maya result, assistant-performed Maya result, and timing measurements. Do not promote one level into another. The old v3 static report missed scope resolution; it is superseded, not proof of correctness.

Provide a file that exists, the exact public compound name, required toolkit dependencies and the intended output. Use a new versioned name for a repair and a fresh instance for testing; preserve the user's successful loading workflow. Keep optional mesh expansion out of the interactive test. Avoid speculative install instructions when the actual failure is inside the graph.


## Constants on multi-input ports

Never put a `values` entry on a multi-input child, such as `add.first.in_1` or `multiply.first.b`, i.e. any child listed in the node's `multiInPortNames`. Bifrost drops it and treats the child as 0, with no error (see `regression-history.md`, Case E). Add a value node and connect it instead:

```json
{"nodeName": "two", "valueType": "float"}                                  // in compoundNodes
{"valueName": "two.value", "valueType": "float", "value": "2f"}             // in values
{"source": "two.output", "target": "times_two.first.in_1"}                  // in connections
```

Use the same pattern for a constant array that should auto-loop through a scalar operator. Literals are fine on ordinary named ports (`create_mesh_cube.width`) and on ports that are already array-typed. `validate_native_graph.py` reports violations as `MULTI_INPUT_CHILD_LITERAL`.
