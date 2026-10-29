# Node gotchas and proven idioms (Bifrost 3.0)

Verified while building CityGen (bifrost_citygen repo) on 2026-10-29 with verify_compound.py and live Maya.

## Type inference
- `Geometry::Strands::resample_strands` won't compile unless its `auto` ports are typed: "The data type could not be inferred for one or more input ports of ...: distance_per_strand, minimum_resample_distance". Give `distance_per_strand` an `array<float>` literal `[]` and `minimum_resample_distance` a float literal.
- `Geometry::Properties::get_geo_property` needs its `type` port given as a literal of the wanted array type, for example `array<float>` `["0f"]` or `array<uint>` `["0U"]` (that one reads `strand_offset`).
- `Core::Logic::not` only has vector-bool overloads (bool2 and up). To invert an `array<bool>`, use `Core::Logic::equal(x, false)`.
- `Core::Logic::if` needs both branches to have the same type. To pick per element between an array and a constant, first broadcast the constant into an array, for example `add(multiply(positions, 0), constant)`.
- `Core::Math::max` outputs `maximum` (and `min` outputs `minimum`), not `output`, while `add`, `subtract`, `multiply` and `divide` output `output`.

## Idioms
- **Is anything within r?** `Geometry::Query::get_closest_point(geometry, positions, use_cutoff_distance=true, cutoff_distance=r).found` gives one bool per query position, vectorised. Use it in place of an O(n×m) loop.
- **Boolean cutters from many segments:** instance a unit `create_mesh_cube` on points carrying `point_orientation` and `point_scale` (`create_instances`), bake them with `Modeling::Instances::bake_instanced_geometry.merged_meshes`, and wire `[slab, cutters]` into `boolean_meshes.meshes` (fan-in, operation `Subtraction`). Proven on a 400 m slab minus 355 overlapping boxes: 24 islands in a few seconds. The output is **triangulated** (about 19k triangles here). Count islands with `Geometry::Mesh::find_mesh_islands.face_island_count`.
- **Consecutive point pairs within strands:** take `strand_offset[1:] - 1` as the sorted last-point indices, then `find_in_sorted_array(value = all point indices).found` marks each strand's last point. Filter it out to get segment start indices.
- **Yaw from a direction:** `axis_angle_to_quaternion(axis (0,1,0), radians = atan_2D(y, x))`. To map +X onto (dx, dz), use `atan_2D(-dz, dx)`. To map +Z onto (dx, dz), use `atan_2D(dx, dz)`.
- **Concatenate arrays:** `flatten_nested_array(build_array(a, b))`.
- **Per-element constant property:** `multiply(length(unit_vectors), value)` gives an array of `value` matching another array's length.
- **Snap to the nearest vertex:** `get_closest_point(...).point_indices` feeds `get_from_array(point_position, ...)` to get the matching vertex positions (`locations` is a sampling handle for `sample_property`, not positions). Mask the result with `.found`.
- **Greedy non-overlap of equal rectangles:** an iterate loop over candidates keeps the accepted centres and fronts as state. Run a 2D separating-axis test of the new rectangle against all kept ones at once (four axes, with `absolute_value(dot(...))` projections), reduce with `any_true_in_array`, and append with `flatten_nested_array(build_array(kept, build_array(new)))`. In CityGen it took overlapping building pairs from 49 to 0 on 138 candidates in about 1 s. Check results outside Bifrost too: `bifrost_citygen/tests/check_overlaps.py` re-runs the SAT on an exported .usda.

## Comparing exported USD
- `export_stage_to_file` writes `.usda` text. Instancer arrays (`positions`, `orientations` as `quath` real first, `scales`, `protoIndices`) can be parsed with stdlib regex for independent checks, without pxr.

## USD pack (verified 2026-10-29, CityGen v007)
- **Instancing referenced assets:** for each asset, `define_usd_reference_from_file(file)` feeds `define_usd_prim(path="/<name>", reference_definitions=[ref])`. Pass those prim definitions to `define_usd_point_instancer.prototype_definitions`, with `instance_id_override` = per-point asset index (the points carry no `point_instance_id`). The prototypes land under `<instancer>/prototypes/<name>`.
- **The prototypes relationship comes out reversed:** definitions [a, b, c] are written as targets [c, b, a], and `protoIndices` index the targets. Feed the definitions through `reverse_array` so that index k is asset k. Check with pxr: `PointInstancer.GetPrototypesRel().GetTargets()`.
- **Prototype paths need a leading `/`.** A bare `name` produced targets like `/City/Buildings/prototypesname`.
- **`export_stage_to_file` flattens.** References are resolved and their content is copied in. To keep the composition arcs, export `USD::Layer::get_root_layer(stage)` with `export_layer_to_file` (`relative_path=false` keeps absolute asset paths).
- **`create_usd_stage.file_format` defaults to `Binary`**, whatever the file extension. Set it to `ASCII` (the UI values are `Binary` and `ASCII`) for text you can grep.
- **Viewing the result:** a `mayaUsdProxyShape` with `.filePath` shows the assets' proxy purpose by default. Set `drawRenderPurpose 1` and `drawProxyPurpose 0` to see render geometry.
- **`export_layer_to_file(relative_path=true)` does not relativise references**, only sublayers. Asset paths stay absolute. Rewrite them afterwards with pxr `UsdUtils.ModifyAssetPaths(layer, fn)` in live Maya (`bifrost_citygen/tools/relativize_usd.py`). When checking that prototypes compose, remember that referenced assets can hold their own PointInstancers, whose prototypes are leaf gprims with no children.
- **Vertex-based distance tests miss long segments.** `get_closest_point` finds the nearest *vertex*, so a polyline with a long straight segment (for example a road end moved by snapping) is invisible along its length. Resample the strands (`resample_strands`, every 2 m) before querying distances.

## Booleans (measured 2026-10-29, CityGen v010)
- `boolean_meshes` time grows with the number of cutter boxes, not with the slab. Halving the boxes (road segments every 36 m instead of 18 m) cut a 1200 m city's block boolean from 10.0 s to 3.3 s with identical islands.
- `fix_self_intersections=false` with overlapping cutters baked into one mesh returns an **empty** mesh. Leave it on whenever the cutters overlap each other.
- For a fast approximate region split, rasterise instead: a `create_mesh_plane` grid, `get_closest_point(...).found` on the face centres (with a cutoff), then `delete_faces(faces_to_delete = that array<bool>)`. This took 0.43 s against 3.3 s at 1200 m, but the edges are stepped at the cell size and small regions can vanish.

## Numbers and literals (2026-10-29, CityGen v011)
- **`to_long` / `to_int` truncate.** `to_long(length(unit_vector))` is often 0, because the length comes out as 0.99999. Use `round_to_nearest` before converting whenever the value should be a whole number. In CityGen this silently relabelled some lots as asset 0 for four versions.
- **Bool values through `cmds.vnnNode(..., setPortDefaultValues=(port, value))`: use `"1"` / `"0"`.** `"true"` was accepted without error but left the port false (seen on `ppg_urban_multistyle_v4_3.usd_write`). In native JSON, the literal `"true"` is fine.
- **Pulling a `BifrostUsd::Stage` output headless:** `bifrost_headless.py` can't read a Stage output. To force a compound's stage (and its export) to evaluate, wire it through `USD::Layer::get_root_layer` and then `get_layer_identifier`, and read that string output.
