# Bifrost reasoning guide

Use this file for cross-cutting rules that matter when designing or debugging Bifrost graphs. Use compact node references for intent; verify exact signatures against working native exports and public compound interfaces. Read `native-json.md` for file format and scope rules. For idiomatic combinations, retrieve Autodesk example graphs.

## Data model

- Treat meshes, points, strands, instances, fields, volumes, skeletons, and generic objects as distinct schemas even when operations can share point-level behavior.
- Treat geometry properties as named data channels. Verify exact property spelling before relying on a property; accidental string differences can create or query the wrong property.
- Prefer array operations and auto-vectorized nodes over element-by-element logic when possible.
- Remember that arrays are zero-indexed.
- Treat fields as lazily evaluated spatial functions; sample them only where values are required.
- Treat level sets as signed-distance representations; negative values are inside and positive values are outside.
- Treat quaternion storage as `(x, y, z, w)` and distinguish position, direction, and normal transforms.
- Treat transform hierarchies as parent-indexed structures; a root parent index is `-1`.

## Graph design

1. Start from data types and required output, not from a favorite node.
2. Identify the minimal dataflow spine first: source → transform/process → solver or assembly → output.
3. Add properties, fields, randomization, shading, caching, and diagnostics as separate concerns.
4. Prefer compounds already demonstrated in Autodesk examples when they closely match the intent.
5. Preserve artist-facing controls at meaningful abstraction boundaries rather than exposing every internal value.
6. When a port accepts an interpreted/auto value, consider whether a scalar, per-element array, field, or property-name string is the most appropriate representation.
7. When a graph is large, reason hierarchically by compound rather than flattening the whole network at once.

## Simulation

- Separate sourcing, solver settings, influences/colliders, simulation, post-process, cache, and render preparation.
- Treat timestep, voxel size, particle spacing, substeps/iterations, and cache behavior as stability/performance controls, not decorative settings.
- For iterative work, build a low-cost preview configuration before increasing resolution.
- Preserve frame/time dependencies and initial-state behavior explicitly.

## Diagnostics and validation

- Use scope/display nodes to inspect intermediate points, meshes, volumes, fields, influences, skeletons, and transforms.
- Validate mesh/point/strand/skeleton structures when construction or conversion is nontrivial.
- Use accelerators for repeated spatial queries.
- Profile expensive sections before proposing micro-optimizations.
- Check terminal/output state and Maya-facing output ports when a graph computes correctly but produces no visible result.

## Version discipline

- Treat the bundled node references and Autodesk graph corpus as versioned evidence, not timeless truth.
- Preserve `library_dependencies` from example graphs when citing a pattern.
- If the user's installed Maya/Bifrost version is known, flag examples whose library versions differ materially rather than assuming exact compatibility.

## Native exports and repeated geometry

Read `native-json.md` for the native-versus-blueprint contract and immediate-scope helper preflight. Read `ppg-building-design.md` for shared prototype modeling, lightweight parallel layout, retained instances, output contracts and isolated optional baking. Treat these as separate design decisions; a small visible graph is not automatically a low-cost evaluated graph.
