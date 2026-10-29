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
