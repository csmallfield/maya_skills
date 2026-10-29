# PPG procedural buildings: design for repeated work

## Contents
- Evidence and scope
- Architecture and edit dependencies
- PPG cuts, tags and orientation
- Retained instances and placement
- Architectural controls and trade-offs
- Diagnostics and performance acceptance

## Evidence and scope

Ground these patterns in the supplied PPG written documentation in `ppg-docs/`, the normalized custom implementations, and the user-confirmed v3.1 example. Consult `regression-history.md` for the failures and evidence levels. Preserve PPG's face-tag and selected-edge terminology. Treat the building architecture below as the design developed in this conversation, not as Roland Reyer's tutorial prescription. No YouTube transcript was retrieved or reviewed.

Prefer the supplied written docs for the meaning of controls, actual interfaces for spelling/type/overload, and source topology for whether an operation copies/merges geometry. Do not infer retained instancing from a compound's name.

## Architecture and edit dependencies

Separate **dimensions**, **prototype modeling**, **layout**, **instancing**, **materials**, and **optional bake**:

```text
controls -> validated tier dimensions -> tier/elevation layout -> placement points
module controls -> one PPG reference bay -> split/shade small material prototypes
structural dimensions -> batched cuboid records -> placement points
prototypes + placement -> native retained instancers -> interactive building
interactive building -> separate optional expansion/bake -> polygon handoff
```

Use the simplest data representation for each stage. Prefer scalar/array math and automatic array processing for regular coordinates; use a divided plane and face centers when it makes the carrier topology easy to inspect. Do not require a PPG cut where a primitive division already solves layout. Use PPG on the detailed module where its face selection, cuts and extrusions add value.

Put repeated topology creation on a small shared source, not on all floor/window faces. Reuse a finite module family for meaningful variation. Keep independent tier/elevation placement in `for_each` loops when needed; do not put a detailed modeling chain or a growing merged-mesh accumulator inside a loop merely to reduce visual node count. Use a stateful iterate only when the design genuinely depends on previous iterations.

Preserve cheap edit paths: changing floor count should change layout rather than rebuild every window; changing module recess should rebuild the shared module; changing global position should change placement. Verify actual invalidation/evaluation behavior in Maya instead of promising caching that has not been measured.

Represent cornices, corner piers, crown pieces and simple entrance components as batched cuboid size/center/material records using a shared unit cube. Keep records parametric, not baked world-space geometry. Name record order and material indices so the compact graph remains maintainable. Add richer prototypes only where the design requires them.

## PPG cuts, tags and orientation

Read `PPG_multi_cut.md`, `PPG_sequence_cut.md`, `get_face_info.md`, `PPG_extrude.md` and `create_pattern.md` before adapting their controls.

- Use **Relative (Quads only)** for supported quad layouts; the written documentation calls it the fast method. Use **Projection** when non-quad/general projected cuts actually require it. Do not apply the quad-only path to unsupported topology.
- Use **Fixed Subdivs** to express a fixed count and choose the flexible strip category intentionally. The docs allow per-source-face arrays for inner/outer widths and subdivision counts. Resolve native numeric mode values from the actual compound; do not assume a dropdown index from its prose order.
- Treat **Sequence Scale** as scaling a size/ratio sequence, not as a floor-count control. Set **Repeat** using the documented `create_pattern` modes. Flexible sequence elements can grow but do not shrink below their specified size. A single sequence can stretch into a few large panels instead of creating storeys. Inspect resulting face counts and module dimensions before detailing.
- Preserve selected-edge semantics. Direction method, point index, next/opposite edge, face orientation and aspect ratio affect the cutting direction. A direction vector is not necessarily active when another method is selected. Verify the four elevations with edge diagnostics; do not assume a world vector works identically on every face.
- Use explicit tags for material/operation domains. Set inheritance deliberately: inherited source names become prefixes, changing later selection expressions. Preserve reference prefixes when using **Store as Reference** / **Use Reference** across child faces. Do not hard-code face IDs after topology changes without an explicit ID-remapping contract.
- Disable intermediate welding and diagnostic terminals when not needed. Keep geometry welded only where the next operation requires it; disjoint modular shells are not automatically a watertight solid. Perform normal/material preparation on prototypes when compatible with the required appearance.

The working reference bay uses three `PPG_extrude` operations and two fixed `PPG_multi_cut` operations: masonry inset, opening recess, mullion/frame divisions and a small glass setback. Inspect exact settings in `nyc_shared_module_library/nyc_ppg_bay_master`; do not rebuild numeric enum mappings from this summary.

## Retained instances and placement

The supplied `PPG::PPG_instance` implementation routes transformed copies through `Modeling::Common::merge_geometry` before its output checks. Its `out_mesh`/`new_geometry` outputs should not be assumed to retain native instances. This observation applies to the supplied implementation, not every future PPG version.

Use the proven `Geometry::Instances::set_instance_geometry` wiring when the required output is retained instances. The example carries:

| Property | Observed type | Role |
|---|---|---|
| `point_position` | `Math::float3` | Placement centers |
| `point_orientation` | `Math::float4` | Quaternion orientation |
| `point_scale` | `Math::float3` | Per-instance nonuniform scale |
| `point_instance_id` | `long` | Prototype/material-variant selection |
| `point_size` | `float` | Explicit uniform size, set to 1 in the final layout |

Read actual property-setting nodes for component domains and scalar/array behavior. Validate positive scales, normalized orientation, handedness, outward-facing panels, pivot alignment, prototype index bounds and equal per-point array lengths. Do not assume the native `point_instance_id` type matches PPG's separate `instance_IDs` input type.

Scale both placement positions and instance sizes exactly once for output-unit conversion; apply final translation in output units. Do not scale the prototype and its instance size again. Keep the module's normal-axis scale independent of bay width/height when recess depth must remain constant.

Split and shade masonry/glass/metal on the shared source before instancing. Keep the output contract explicit: an `Object` mesh, `array<Object>` mesh groups, and an `array<Object>` of instancers are not interchangeable just because their outer types overlap. In v3.1 `building` is four instancers. Keep `module_preview` and `layout_points` as alternatives for diagnostics, not additional copies to display over the building.

Offer expansion as a separate downstream baker only when meshes are required. Do not leave it connected during interactive profiling. Do not promise per-prototype materials survive a merge; inspect/reassign for the destination. The supplied baker is an unconfirmed optional example, not a verified production exporter.

## Architectural controls and trade-offs

Preserve a hierarchy of base/entrance, main shaft, setbacks and crown. Organize repeated bays, strong corners and tier cornices before adding tertiary detail. Use module families or tagged variation rather than per-window branches for superficial variation. The NYC case is inspired by a supplied image, not a measured reconstruction.

Clamp counts and dimensions, prevent negative remaining footprints after setbacks, and bound inset/frame widths against the **actual** cell/module dimensions. Distinguish floor count, storey height, wall margin, frame width and recess depth; do not use arbitrary topology distortion to fit invalid inputs.

Disclose the v3.1 trade-off: its 4 by 3.6 reference bay stretches in-plane. Frame widths and masonry margins scale with that stretch; recess depth does not stretch with bay width/height. To preserve absolute frame widths, build a small family keyed by distinct physical bay dimensions, or use separately scaled subcomponents. Do not return to unique per-window topology by default.

Treat exterior assemblies, intersections, repeated UVs and absence of interior geometry as declared output limitations. Do not describe the example as a watertight simulation mesh or finished hero asset.

## Diagnostics and performance acceptance

Inspect, in order: dimensions -> carrier counts -> orientation/scale -> one detailed bay -> prototype/material split -> retained instances -> optional bake. Display only one diagnostic/output representation at a time.

Count evaluated modeling invocations and source faces, not just root nodes or JSON size. The design comparison is 8 full-panel PPG chains / 416 initial cells in v2 versus 1 small chain / 1 source cell in v3.1. Each chain has five PPG modeling nodes. These are construction counts, not timing ratios. The scope repair duplicated a definition without adding a call.

Record user feedback precisely: v3.1 was reported to work "much much better". No numeric timing, speedup multiplier, memory measurement or renderer coverage was supplied. Do not present that feedback as an assistant-run benchmark.

For new benchmarks, separate initial compilation, warm parameter evaluation, viewport update and bake. Disconnect the older version and baker. Compare a layout edit, a module edit and placement/scale edits at the same output detail. Increasing instance count still has placement/display cost; retained instancing removes repeated detailed topology work, not all growth with building size.

## PPG USD exports carry placement metadata (user files, generator 4.3, read 2026-10-29)

The user's PPG building exports (`/Building` default prim, binary .usdc) store `citygenInput:*` custom **attributes** on `/Building` (not customData; read them with `prim.GetAttributes()`): `storeys`, `frontLocal` (0,0,1), `entranceLocal`, `usage`, `selectionWeight`, `minBuildingGapM`, `minStreetSetbackM`, plus `facadeId`, `footprintId`, `massingId` and version keys. There is no footprint size; take it from the bounds of `/Building/Proxy` (the render bounds add about 0.9 m of storefront overhang). Values are in metres, but the stage declares `metersPerUnit` 0.01, so resolve the scale before referencing these files into a metre-based scene. Inside, `/Building/Render` already uses per-material PointInstancers. Read them with pxr in live Maya (`maya_exec.py`), since `mayapy -I` has no pxr.
