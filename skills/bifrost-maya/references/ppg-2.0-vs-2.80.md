# PPG 2.0 vs installed PPG 2.80 beta1

The compound corpus in `compound-data/` is built from the user's installed **PPG_V2.80_beta1** (`~/Autodesk/Bifrost/Compounds`), which replaced the PPG 2.0 copy Astra used. VHH and the other libraries were byte-identical, and the 34 PPG Markdown docs in `ppg-docs/` are unchanged between the two versions. Generated 2026-10-29 by comparing the two interface indexes.

Treat interfaces from the corpus as 2.80. Graphs authored against 2.0 still load, but check the changed ports below.

## New in 2.80

- `PPG::Hyuu::autoport_to_array`
- `PPG::Hyuu::face_vertex_slice`
- `PPG::Hyuu::is_odd`
- `PPG::Hyuu::random_value_array_range`
- `PPG::MJCG::angle_between_vectors`
- `PPG::bulk_rename`
- `PPG::get_maya_face_tags`
- `PPG::group_face_tags`

## Only in 2.0 (renamed or removed in 2.80)

- `Hyuu::Geometry::Properties::face_vertex_slice`
- `Hyuu::Logic::is_odd`
- `Hyuu::Utility::autoport_to_array`
- `Hyuu::merge_vertices_clean`
- `MJCG::Core::Math::angle_between_vectors`

The Hyuu and MJCG helpers moved under the `PPG::` namespace (for example `Hyuu::Logic::is_odd` became `PPG::Hyuu::is_odd`). `Hyuu::merge_vertices_clean` has no 2.80 counterpart under that name.

## Interface changes in shared compounds

- **PPG::PPG_arch**: added `scale` (input, float)
- **PPG::PPG_chip_off**: added `scale` (input, float)
- **PPG::PPG_dome**: added `global_scale` (input, float)
- **PPG::PPG_extrude**: added `offset` (input, auto), `scale` (input, float); removed `offset` (input, float)
- **PPG::PPG_instance**: added `scale` (input, float)
- **PPG::PPG_multi_cut**: added `scale` (input, float)
- **PPG::PPG_multi_instance**: added `scale` (input, float)
- **PPG::PPG_sequence_cut**: added `scale` (input, float)
- **PPG::PPG_transform**: added `global_scale` (input, float)
- **PPG::PPG_wedge**: added `scale` (input, float)
- **PPG::cluster_values**: added `remainder_propagation` (input, bool)
- **PPG::display_selected_edges**: added `scale` (input, float)
- **PPG::edge_selection**: added `dcc_name` (output, auto), `face_uvSet_UV` (output, auto)
- **PPG::rename_face_tag**: added `replace_this_string` (input, string)
- **PPG::set_face_ID_tags**: added `inherit_source_tag` (input, bool)

Most PPG operators gained a `scale` or `global_scale` float input. `PPG_extrude.offset` changed from `float` to untyped (`auto`), so connect a matching type deliberately.
