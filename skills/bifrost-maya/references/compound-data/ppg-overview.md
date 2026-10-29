# PPG 2.0 Compound Reference

Normalized files: **74**

## Categories

### compounds (54)
- **PPG::PPG_arch** (`PPG_V2.0__compounds__PPG_arch`) — Builds an arch on every selected face (equiangular planar quads only).
- **PPG::PPG_chip_off** (`PPG_V2.0__compounds__PPG_chip_off`)
- **PPG::PPG_diagnostc** (`PPG_V2.0__compounds__PPG_diagnostc`) — Diagnostic display for PPG specific face tags.
- **PPG::PPG_dome** (`PPG_V2.0__compounds__PPG_dome`) — Creates a multi segment extrude on selected faces. Lets you create domes or bulbous spires.
- **PPG::PPG_extrude** (`PPG_V2.0__compounds__PPG_extrude`) — Extrude selected faces. Many thanks to user "HeyUU" of the Bifrost Addicts community on Discord for this extrude in PPG1.0 and for some cool code in PPG2.0.
- **PPG::PPG_instance** (`PPG_V2.0__compounds__PPG_instance`) — Replaces selected faces with instance objects. The instance objects are scaled and oriented according to the respective face.
- **PPG::PPG_multi_cut** (`PPG_V2.0__compounds__PPG_multi_cut`) — Cuts selected quad polygons into strips with an odd/even pattern.
- **PPG::PPG_multi_instance** (`PPG_V2.0__compounds__PPG_multi_instance`) — Replaces selected faces with a ROW of instance objects.
- **PPG::PPG_sequence_cut** (`PPG_V2.0__compounds__PPG_sequence_cut`) — Cuts selected quad polygons into strips with given patten of widths.
- **PPG::PPG_shader** (`PPG_V2.0__compounds__PPG_shader`)
- **PPG::PPG_transform** (`PPG_V2.0__compounds__PPG_transform`) — Transforms selected faces or their selected edges.
- **PPG::PPG_wedge** (`PPG_V2.0__compounds__PPG_wedge`) — Creates a wedge from selected faces around their selected edges.
- **PPG::assign_manual_colors** (`PPG_V2.0__compounds__assign_manual_colors`)
- **PPG::assign_material_to_tags** (`PPG_V2.0__compounds__assign_material_to_tags`) — Splits the selectd faces off the object and assigns a material reference. Outputs the new faces with material reference and the remaining rest object.
- **PPG::assign_random_colors** (`PPG_V2.0__compounds__assign_random_colors`)
- **PPG::bulk_assign_material** (`PPG_V2.0__compounds__bulk_assign_material`) — Assigns material references to multiple face groups.
- **PPG::check_face_tags** (`PPG_V2.0__compounds__check_face_tags`)
- **PPG::cluster_values** (`PPG_V2.0__compounds__cluster_values`) — Lets you build groups of values that are similar. Example: - Face IDs need to be grouped together based on the Y position of the face centers. - The Face IDs are fed into 'Values to Cluster'. - The Y component of the according face centers is fed into 'Cluster Value' - All Face IDs whos Y position is within the tolerance are grouped and output as a 2-dimensional array.
- **PPG::create_arch** (`PPG_V2.0__compounds__create_arch`) — Experimental node. Creates an arch window for instancing.
- **PPG::create_pattern** (`PPG_V2.0__compounds__create_pattern`) — Repeats a sequence in various ways.
- **PPG::display_face_tags** (`PPG_V2.0__compounds__display_face_tags`)
- **PPG::display_selected_edges** (`PPG_V2.0__compounds__display_selected_edges`)
- **PPG::edge_selection** (`PPG_V2.0__compounds__edge_selection`)
- **PPG::face_tag_renamer** (`PPG_V2.0__compounds__face_tag_renamer`)
- **PPG::faces_ID_input** (`PPG_V2.0__compounds__faces_ID_input`) — Lets you input the face numbers.
- **PPG::faces_from_origin_XZ** (`PPG_V2.0__compounds__faces_from_origin_XZ`)
- **PPG::faces_to_origin_XZ** (`PPG_V2.0__compounds__faces_to_origin_XZ`)
- **PPG::get_all_faces** (`PPG_V2.0__compounds__get_all_faces`)
- **PPG::get_face_indices** (`PPG_V2.0__compounds__get_face_indices`)
- **PPG::get_face_info** (`PPG_V2.0__compounds__get_face_info`) — Outputs information about the selected faces.
- **PPG::get_face_orientation** (`PPG_V2.0__compounds__get_face_orientation`)
- **PPG::get_faces_from_tags** (`PPG_V2.0__compounds__get_faces_from_tags`) — Returns the faces that belong to tag(s).
- **PPG::get_maya_component_tags** (`PPG_V2.0__compounds__get_maya_component_tags`) — Not supported in Bifrost 2.7.0. Get Maya component tags.
- **PPG::get_points_per_face** (`PPG_V2.0__compounds__get_points_per_face`)
- **PPG::get_tag_faces** (`PPG_V2.0__compounds__get_tag_faces`) — Returns the faces for one specific tag.
- **PPG::match_expression** (`PPG_V2.0__compounds__match_expression`) — Checks whether a string name matches the expression input. This is useful for filtering property names using wildcards. Some example expressions: + To match: + all strings use: + strings that start with "point " OR end with "index" use: point index + all strings AND NOT those that end with "normal" use: ! normal + strings that contain "point" use: point
- **Hyuu::merge_vertices_clean** (`PPG_V2.0__compounds__merge_vertices_clean`)
- **PPG::merge_vertices_clean_tags** (`PPG_V2.0__compounds__merge_vertices_clean_tags`)
- **PPG::new_face_tag** (`PPG_V2.0__compounds__new_face_tag`) — Set the face tag for a selection of faces. This is a combination of "get faces from tags" and "set face tag".
- **PPG::pattern_rename** (`PPG_V2.0__compounds__pattern_rename`) — Sets PPG face tags for the provided face IDs. Creates a pattern of names from the list in 'Pattern'.
- **PPG::remove_A_from_B** (`PPG_V2.0__compounds__remove_A_from_B`)
- **PPG::rename_face_tag** (`PPG_V2.0__compounds__rename_face_tag`)
- **PPG::reverse_faces** (`PPG_V2.0__compounds__reverse_faces`)
- **PPG::rewrite_face_tags** (`PPG_V2.0__compounds__rewrite_face_tags`)
- **PPG::select_faces_by_area** (`PPG_V2.0__compounds__select_faces_by_area`) — Filters given faces by their area.
- **PPG::select_faces_by_field** (`PPG_V2.0__compounds__select_faces_by_field`) — Select faces using a field.
- **PPG::select_faces_by_normal** (`PPG_V2.0__compounds__select_faces_by_normal`) — Filters given faces by their normal.
- **PPG::select_faces_by_shape** (`PPG_V2.0__compounds__select_faces_by_shape`) — Filters given faces by their properties.
- **PPG::select_faces_by_visibility** (`PPG_V2.0__compounds__select_faces_by_visibility`) — Filters given faces by their visibility from given viewpoints.
- **PPG::select_faces_inside_mesh** (`PPG_V2.0__compounds__select_faces_inside_mesh`) — Filters given faces by their position inside/outside of a mesh.
- **PPG::select_random_faces** (`PPG_V2.0__compounds__select_random_faces`) — Selects faces randomly.
- **PPG::set_face_ID_tags** (`PPG_V2.0__compounds__set_face_ID_tags`) — Set the face tags base of the face ID. The resulting tags are numbers (the face ID) with an optional prefix.
- **PPG::set_face_color** (`PPG_V2.0__compounds__set_face_color`)
- **PPG::set_face_tag** (`PPG_V2.0__compounds__set_face_tag`) — Set the face tag for faces in "Face IDs".

### compounds/supporting compounds (20)
- **MJCG::Core::Math::angle_between_vectors** (`PPG_V2.0__compounds__supporting_compounds__angle_between_vectors`)
- **Print::any_array_min_max** (`PPG_V2.0__compounds__supporting_compounds__any_array_min_max`)
- **Print::any_to_string** (`PPG_V2.0__compounds__supporting_compounds__any_to_string`)
- **Print::array_info_string** (`PPG_V2.0__compounds__supporting_compounds__array_info_string`)
- **Print::array_min_max** (`PPG_V2.0__compounds__supporting_compounds__array_min_max`)
- **Hyuu::Utility::autoport_to_array** (`PPG_V2.0__compounds__supporting_compounds__autoport_to_array`)
- **User::Compounds::case** (`PPG_V2.0__compounds__supporting_compounds__case`)
- **Print::commands_and_palette** (`PPG_V2.0__compounds__supporting_compounds__commands_and_palette`)
- **Print::create_fast_text_NF** (`PPG_V2.0__compounds__supporting_compounds__create_fast_text_NF`)
- **Print::degrees_to_quaternion** (`PPG_V2.0__compounds__supporting_compounds__degrees_to_quaternion`)
- **Hyuu::Geometry::Properties::face_vertex_slice** (`PPG_V2.0__compounds__supporting_compounds__face_vertex_slice`)
- **Print::float_to_string** (`PPG_V2.0__compounds__supporting_compounds__float_to_string`)
- **Print::hex_color_palette** (`PPG_V2.0__compounds__supporting_compounds__hex_color_palette`)
- **Hyuu::Logic::is_odd** (`PPG_V2.0__compounds__supporting_compounds__is_odd`)
- **Print::quaternion_to_degrees** (`PPG_V2.0__compounds__supporting_compounds__quaternion_to_degrees`)
- **Print::set_print_material** (`PPG_V2.0__compounds__supporting_compounds__set_print_material`)
- **Print::string_to_ASCII** (`PPG_V2.0__compounds__supporting_compounds__string_to_ASCII`)
- **Print::test_for_changes** (`PPG_V2.0__compounds__supporting_compounds__test_for_changes`)
- **Print::value_to_hex** (`PPG_V2.0__compounds__supporting_compounds__value_to_hex`)
- **Print::value_to_string** (`PPG_V2.0__compounds__supporting_compounds__value_to_string`)
