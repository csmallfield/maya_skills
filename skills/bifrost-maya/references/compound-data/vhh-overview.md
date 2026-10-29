# VHH Compound Reference

Normalized files: **133**

## Categories

### geo (30)
- **VHH::Core::Geometry::along_strand** (`VHH__geo__along_strand`) — This compound is a solver that moves a point along a strand at a given speed.
- **VHH::Core::Geometry::bend_strand** (`VHH__geo__bend_strand`) — performs a circular bend on an input strand
- **VHH::Core::Geometry::bezier** (`VHH__geo__bezier`) — generates a bezier curve based on 2 anchor points and control points
- **VHH::Core::Geometry::BF_connectivity** (`VHH__geo__bf_connectivity`) — When a mesh or object has islands (connected pieces of the mesh that may not be connected to each other) this compound will assign an id to each of the points or the faces in those islands, per island. This is a similar result to Houdini's connectivity node
- **VHH::Core::Geometry::bounds** (`VHH__geo__bounds`) — Generates and returns a bounding object for a geometry.
- **VHH::Core::Geometry::construct_circle** (`VHH__geo__construct_circle`) — This compound makes a closed circle.
- **VHH::Core::Geometry::curve_road** (`VHH__geo__curve_road`) — Ribbon generator, with banking, version 1. No UVs yet
- **VHH::Core::Geometry::delete_components_by_volume** (`VHH__geo__delete_components_by_volume`) — This compound deletes faces (by default) or points based on whether those points are inside an object. It will also generate scatter weights for that object to exclude the culled components. Because it's interanlly based on a volume, you are able to erode/grow the volume.
- **VHH::Core::Geometry::exploded_view** (`VHH__geo__exploded_view`)
- **VHH::Core::Geometry::extrude_and_average** (`VHH__geo__extrude_and_average`) — Taking in an array of meshes, this compound will use the extrude and median property blur compounds. Extruding and averaging the verticies of the incoming array. Note: this compound is auto-looped, so while the mesh array input looks like a single mesh input, it wants an array.
- **VHH::Core::Geometry::extrude_loop** (`VHH__geo__extrude_loop`) — This compound will extrude the selected faces in a iteration loop. It allows you to fake a bevelled look, without actually doing anything as helllishly complicated as an actual bevel.
- **VHH::Core::Geometry::fib_sphere** (`VHH__geo__fib_sphere`) — Distributing points evenly on a sphere by creating a Fibonacci lattice, based on this article: http://extremelearning.com.au/how-to-evenly-distribute-points-on-a-sphere-more-effectively-than-the-canonical-fibonacci-lattice/
- **VHH::Core::Geometry::get_face_centers** (`VHH__geo__get_face_centers`) — When an object containing faces is connected to this compound, it will return the face center positions as a geo property on the object, and a float3 array. It will also return the face indicies as a 2d uint array. This compound only works on meshes. If an object without faces is connected (points, strand etc) the object will pass through the compound unchanged.
- **VHH::Core::Geometry::mapUV_auto_six** (`VHH__geo__mapUV_auto_six`) — Generates and applies a basic six-axis UV projection along x, y, z, and -x, -y, -z axiis.
- **VHH::Core::Geometry::mapUV_from_camera** (`VHH__geo__mapUV_from_camera`) — Projection mapped UV from a camera position
- **VHH::Core::Geometry::property_gradient** (`VHH__geo__property_gradient`) — This compound returns the gradient of a geo property as vectors.
- **VHH::Core::Geometry::proximity_sort** (`VHH__geo__proximity_sort`) — Sorts and displays points by proximity to another point.
- **VHH::Core::Geometry::rockify** (`VHH__geo__rockify`) — Using noise and displacement, turn anything into a rock, or at least a stony-looking blob. [ rockify workflow ](https://youtu.be/rqklfVhOtvA)
- **VHH::Core::Geometry::setup_strand_properties** (`VHH__geo__setup_strand_properties`) — A compound for quickly setting up useful properties on an incoming strand.
- **VHH::Core::Geometry::split_strand_by_property** (`VHH__geo__split_strand_by_property`) — Splits a single strand into multiple strand by a given property.
- **VHH::Core::Geometry::split_strand_by_random** (`VHH__geo__split_strand_by_random`) — Splits a single strand into multiple strands by a random amount.
- **VHH::Core::Geometry::split_strands** (`VHH__geo__split_strands`) — Splits a single strand into multiple strands. If the input only contains a single strand, only a single strand will be output.
- **VHH::Core::Geometry::strand_to_mesh** (`VHH__geo__strand_to_mesh`) — Converts a strand to a mesh using tube or ribbon extrusion. It takes into account the point size property for the thinkness of the extrusions, and allows you to set a base, minimum and maximum width. Uses compounds from both Maxime Jeanmougin and Aslan Jafari with all thanks and credit to them.
- **VHH::Core::Geometry::sweep_strand** (`VHH__geo__sweep_strand`) — Sweep a strand along it's length.
- **VHH::Core::Geometry::update_point_curvature** (`VHH__geo__update_point_curvature`) — This compound uses vertex-to-edge average calculations to return a curvature value between 0 and 1. It works on strands and meshes while all other data types are passed through unchanged..
- **VHH::Core::Geometry::update_point_density** (`VHH__geo__update_point_density`) — Local point density property generated based on number of point neighbors within a radius.
- **VHH::Core::Geometry::update_point_gradient** (`VHH__geo__update_point_gradient`) — Calculates the gradient of the points based on ascent or descent.
- **User::Compounds::vertical_stack** (`VHH__geo__vertical_stack`) — This compound stacks meshes vertically, with various controls for size control, randomization, rotation etc.
- **VHH::Core::Geometry::voro_split** (`VHH__geo__voro_split`) — This compound splits a mesh based on a voronoi pattern. Note. This does not split faces, it breaks up the mesh according it's existing structure. This means that the final result is heavily dependent on the mesh resolution. If you want a higher resolution mesh I would recoomend converting to volume and back, this compound works fast.
- **VHH::Core::Geometry::wire_deform** (`VHH__geo__wire_deform`) — deforms a mesh by a strand based on closest points

### tool (30)
- **VHH::Tool::AO_filter** (`VHH__tool__AO_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Ambient Occlusion - One of the pre-made input filters. This filters scatter weights by the ambient occlusion of the scatter mesh. Note: This is, by it's nature, extremely slow - use with caution.
- **VHH::Tool::AOBox** (`VHH__tool__aoBox`) — Generate ambient occlusion and assign it to the point color as a float4 (RGBA). Also included are x, y, and z bounding box gradients. AO is calculated by raycasting and as such, this compound can get quite heavy. This compound will output to both a mesh, and as a usd asset.
- **VHH::Tool::camera_occlude_filter** (`VHH__tool__camera_occlude_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Camera Occlusion - One of the pre-made input filters. This filters scatter weights based on the position and view direction of a camera. Any points not seen by the camera will have zero weight.
- **VHH::Tool::curvature_filter** (`VHH__tool__curvature_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Curvature - One of the pre-made input filters. This filters scatter weights based on the curvature values of the input mesh.
- **VHH::Tool::displacer** (`VHH__tool__displacer`) — Component Compound - this compound is a component in the the displacer ecosystem. displacer - This is the main control compound for the displacer system. The Diagnostic tab on this node will display the low-res representation of your heightfield. The Final tab is for rendering the higher-res in Arnold. This is setup internally for you, and will use an internal shader if none is plugged in.
- **VHH::Tool::file_path** (`VHH__tool__file_path`)
- **VHH::Tool::gradient_filter** (`VHH__tool__gradient_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Curvature - One of the pre-made input filters. This filters scatter weights based the curvature values of the input mesh.
- **VHH::Tool::height_filter** (`VHH__tool__height_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter Mesh Height - One of the pre-made input filters. This filters scatter weights based on the y position of the scatter mesh.
- **VHH::Tool::image_filter** (`VHH__tool__image_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Input Image - One of the pre-made input filters. This filters scatter weights by the channels of an input image file.
- **VHH::Tool::import_image** (`VHH__tool__import_image`) — Component Compound - this compound is a component in the displacer ecosystem. Import Image - Compound that carries image displacement information into the displacer compound.
- **VHH::Tool::noise2d_billow** (`VHH__tool__noise2d_billow`) — Component Compound - this compound is a component in the the displacer ecosystem. Billow/Ridge Noise - One of the pre-made noise fields. This is a standard fractal noise with the ability to create a billowing noise or a ridged noise.
- **VHH::Tool::noise2d_cell** (`VHH__tool__noise2d_cell`) — Component Compound - this compound is a component in the the displacer ecosystem. Cellular Noise - One of the pre-made noise fields. This is a single frequency cellular noise similar to Worley noise. Full Credit to Duncan Brinsmead for the math.
- **VHH::Tool::noise2d_curl** (`VHH__tool__noise2d_curl`) — Component Compound - this compound is a component in the the displacer ecosystem. Curl Noise - One of the pre-made noise fields. This is a standard 3d curl noise flattened in various ways for use as a scalar field.
- **VHH::Tool::noise2d_fractal** (`VHH__tool__noise2d_fractal`) — Component Compound - this compound is a component in the the displacer ecosystem. Fractal Noise - One of the pre-made noise fields. The default fractal noise field.
- **VHH::Tool::noise2d_fractal_cell** (`VHH__tool__noise2d_fractal_cell`) — Component Compound - this compound is a component in the the displacer ecosystem. Sine - One of the pre-made fields. This is a cellular field with an inbuild FBM system, letting you have levels of noise..
- **VHH::Tool::noise2d_simplex** (`VHH__tool__noise2d_simplex`) — Component Compound - this compound is a component in the the displacer ecosystem. Cellular Noise - One of the pre-made noise fields. This is a simple 2d simplex field.
- **VHH::Tool::noise2d_sine** (`VHH__tool__noise2d_sine`) — Component Compound - this compound is a component in the the displacer ecosystem. Sine - One of the pre-made fields. This is not technically a noise but a sine operation on the field.
- **VHH::Tool::noise3d_curl** (`VHH__tool__noise3d_curl`) — Component Compound - this compound is a component in the the displacer ecosystem. Curl Noise - One of the pre-made fields. This is the default curl noise field.
- **VHH::Tool::noise3d_curve** (`VHH__tool__noise3d_curve`) — Component Compound - this compound is a component in the the displacer ecosystem. Curve Displace - One of the pre-made fields. This displace ther directions of the field based on a strand input
- **VHH::Tool::noise3d_direction** (`VHH__tool__noise3d_direction`) — Component Compound - this compound is a component in the the displacer ecosystem. Direction Field - One of the pre-made fields. This is a simple field for changing the direction of the displacement. Noise may be added to it
- **VHH::Tool::noise3d_outward** (`VHH__tool__noise3d_outward`) — Component Compound - this compound is a component in the the displacer ecosystem. Radial Axis - One of the pre-made fields. This will generate a vector field that pushed outwards from a point.
- **VHH::Tool::noise3d_radial_axis** (`VHH__tool__noise3d_radial_axis`) — Component Compound - this compound is a component in the the displacer ecosystem. Radial Axis - One of the pre-made fields. This will generate a vector field that revolves around an axis.
- **VHH::Tool::noise3d_turbulence** (`VHH__tool__noise3d_turbulence`) — Component Compound - this compound is a component in the the displacer ecosystem. Fractal Turbulence Field - One of the pre-made fields. This is the default fractal turbulence field
- **VHH::Tool::optimised_AO** (`VHH__tool__optimised_ao`)
- **VHH::Tool::rotate_thing** (`VHH__tool__rotate_thing`) — This compound ... rotates things. Works with mesh, strands and points. Animated or just rotated, the possibilities are endless!
- **VHH::Tool::scalar_crater** (`VHH__tool__scalar_crater`) — Component Compound - this compound is a component in the the displacer ecosystem. Scalar Crater - One of the pre-made noise fields. This is a 2d-based (height) field that generates a crater style-displacement. This can get slow.
- **VHH::Tool::scatter_plus** (`VHH__tool__scatter_plus`) — Scatter+ is an attempt to extend scatter functionality. It implements 3 more scatter types, introduces the concept of filtering and includes clustering, automatic point id by color and value, filter and culling by weight. Unlike scatter points the weights are visible and the schema is black = zero weight, white = full weights. When the diagnostic tab is on, the points will be displayed with their weights as a color. The points can be culled inside Scatter+ or externally based on the point weight
- **VHH::Tool::steep_filter** (`VHH__tool__steep_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter Mesh Steepness - One of the pre-made input filters. This filters scatter weights based on the angle of the normals of the scatter mesh.
- **VHH::Tool::tag_filter** (`VHH__tool__tag_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Component Tags - One of the pre-made input filters. This filters scatter weights by tags found or supplied on the imput mesh.
- **VHH::Tool::vector_filter** (`VHH__tool__vector_filter`) — Component Compound - this compound is a component in the the scatter plus ecosystem. Filter by Vector - One of the pre-made input filters. This filters scatter weights bbased on a vector.

### math (19)
- **VHH::Core::Math::find_point_on_line** (`VHH__math__find_point_on_line`) — given the start and the end points of a line and another point, this compound returns the point position on the line.
- **VHH::Core::Math::fractal_tiling_noise** (`VHH__math__fractal_tiling_noise`) — A seamless tiling noise compound.
- **VHH::Core::Math::gauss** (`VHH__math__gauss`) — Given a size value, returns a gaussian (normal) distribution in an array (size value).
- **VHH::Core::Math::gaussian_property_blur** (`VHH__math__gaussian_property_blur`) — Blurs the property data based on a Gaussian Kernel
- **VHH::Core::Math::make_rot_matrix** (`VHH__math__make_rot_matrix`) — constructor for matrices around all three axies
- **VHH::Core::Math::make_value, VHH::Core::Math::make_value, VHH::Core::Math::make_value, VHH::Core::Math::make_value, VHH::Core::Math::make_value, VHH::Core::Math::make_value, VHH::Core::Math::make_value** (`VHH__math__make_value`) — This compound allows you to quickly create a single value, or an array of values quickly. Currently supports string, boolean, float, float3, int, long and matrix4 values.
- **VHH::Core::Math::median_property_blur** (`VHH__math__median_property_blur`) — Blurs the property data based on an average of the neighbors.
- **VHH::Core::Math::point_inside_sphere** (`VHH__math__point_inside_sphere`)
- **VHH::Core::Math::prime_sequence** (`VHH__math__prime_sequence`) — Generates a sequence of prime numbers.
- **VHH::Core::Math::quat_to_forward** (`VHH__math__quat_to_forward`) — Transforms the input quaternion to a forward vector.
- **VHH::Core::Math::quat_to_left** (`VHH__math__quat_to_left`) — Transforms the input quaternion to a sideways vector.
- **VHH::Core::Math::quat_to_up** (`VHH__math__quat_to_up`) — Transforms the input quaternion to a upwards vector.
- **VHH::Core::Math::RK4_Solver** (`VHH__math__rk4_solver`)
- **VHH::Core::Math::round_to** (`VHH__math__round_to`) — Rounds a floating point number to n decimal places. Outputs float and string.
- **VHH::Core::Math::set_range, VHH::Core::Math::set_range** (`VHH__math__set_range`)
- **VHH::Core::Math::tiling_noise** (`VHH__math__tiling_noise`) — A seamless tiling noise compound.
- **VHH::Core::Math::vector_to_color** (`VHH__math__vector_to_color`) — Takes a float3 vector or a vector field and returns a color value inside the 0-1 ranges.
- **VHH::Core::Math::vector_to_color** (`VHH__math__vector_to_color.jason`) — Takes a float3 vector or a vector field and returns a color value inside the 0-1 ranges.
- **VHH::Core::Math::weighted_average** (`VHH__math__weighted_average`) — Similar to a "normal" average, except that instead of each of the inputs contributing equally to the final average, one input contributes more than the other. Average with bias.

### display (14)
- **VHH::Visualize::Display::HSV_to_RGB** (`VHH__display__HSV2RGB`)
- **VHH::Visualize::Display::RGB** (`VHH__display__RGB`)
- **VHH::Visualize::Display::RGB_to_HSV** (`VHH__display__RGB2HSV`)
- **VHH::Visualize::Display::RGBA** (`VHH__display__RGBA`)
- **VHH::Visualize::Display::eval_fCurve_with_mag** (`VHH__display__eval_fCurve_with_mag`) — Allows for the evaluation of an fCurve compound with a multiplier (magnitude) while offering both full range (input\ magnitude) and normalized (0-1 \ magnitude) output.
- **VHH::Visualize::Display::fresnel_viz** (`VHH__display__fresnel_viz`) — Applies a fresnel effect to the vertex color. The fresnel effect changes the colour of the vertex based on the incident angle to the camera. Requires a camera world matrix input. Big thanks to [Ronja's tutorials.](https://www.ronja-tutorials.com/post/012-fresnel/)
- **VHH::Visualize::Display::gnomon** (`VHH__display__gnomon`) — Produces the CG gnomon at origin.
- **ValHallen::Helpers::nPointRamp** (`VHH__display__nPointRamp`) — This compound generates a ramp from an array of colours based on an input ramp.
- **VHH::Visualize::Display::pnt_display** (`VHH__display__pnt_display`) — quick point display node
- **VHH::Visualize::Display::point_color_by_property** (`VHH__display__point_color_by_property`) — Allows you to visualise and edit a property on an object. Useful for visualization and some basic tweaking. Supports long, float and vector properties.
- **VHH::Visualize::Display::pos_display** (`VHH__display__pos_display`) — This compound displays position vectors as points.
- **VHH::Visualize::Display::ramp** (`VHH__display__ramp`) — This compound generates a ramp output based on several criteria. It outputs both the color per vertex and the geometry with a colour property written to it. [ ramp (youtube) ](https://youtu.be/S5Kzf1-eiuU)
- **VHH::Visualize::Display::show_normals** (`VHH__display__show_normals`) — Displays the point or face normals of a mesh.
- **VHH::Visualize::Display::ramp_switch** (`VHH__display__switch_ramp`) — This compounds enables switching between several ramp presets, or inputting a custom ramp.

### LightBox/compounds (10)
- **VHH::Tool::LB_AO** (`VHH__LightBox__compounds__LB_AO`) — Component Compound - this compound is a component in the the LightBox system. LB AO - This is a compound that generates an ambient occlusion value to be multiplied onto the lighting information. As this is calculated by multiple raycasts per point , the more points you have in your mesh, or the higher the resolution setting, the slower this will go. It's as fast as I can make it, for now, and it can be set to only compute on a single frame, so this can help.
- **VHH::Tool::LB_ambient** (`VHH__LightBox__compounds__LB_ambient`) — Component Compound - this compound is a light in the the LightBox system. Ambientlight - This is a diffuse light generator that mimics the lighting from an ambient light. It does this by applying a flat colour to the entire mesh.
- **VHH::Tool::LB_area** (`VHH__LightBox__compounds__LB_area`) — Component Compound - this compound is a light in the the LightBox system. Arealight - This is a diffuse light generator that mimics the lighting from an area light. It does this by taking the light direction and the mesh surface normal, performing a dot product and multiplying by the light's intensity. The area light is made by using projections and sampling, therefore has more settings used in creating shadow information.
- **VHH::Tool::LB_directional** (`VHH__LightBox__compounds__LB_directional`) — Component Compound - this compound is a light in the the LightBox system. Directionallight - This is a diffuse light generator that mimics the lighting from a directional light. It does this by taking the light direction and the mesh surface normal, performing a dot product and multiplying by the light's intensity. Then applying shadow information.
- **VHH::Tool::LB_display** (`VHH__LightBox__compounds__LB_display`) — Component Compound - this compound is a component in the the LightBox system. LB display - the end of the chain for lightbox. This compound handles both display and output of your lighting system. The lighting and AO information is stored on the verts, and can be output in 2 ways. There's mesh out that can be sent to an output node, then converted to a Maya mesh as usual and exported as FBX etc. Then there's the USD output built into the interior of the node. This can be turned on and off on the
- **VHH::Tool::LB_gradient** (`VHH__LightBox__compounds__LB_gradient`)
- **VHH::Tool::LB_locator_transform** (`VHH__LightBox__compounds__LB_locator_transform`) — Component Compound - this compound is a component in the the LightBox system. LB locator transform - this is a simple compound that converts an incoming world matrix to a position and direction vector - these are used in the lights.
- **VHH::Tool::LB_pointlight** (`VHH__LightBox__compounds__LB_pointlight`) — Component Compound - this compound is a light in the the LightBox system. Pointlight - This is a diffuse light generator that mimics the lighting from a point light. It does this by taking the direction from each point to the light and the mesh surface normal, performing a dot product and multiplying by the light's intensity. Then applying shadow information.
- **VHH::Tool::LB_skydome** (`VHH__LightBox__compounds__LB_skydome`) — Component Compound - this compound is a light in the the LightBox system. Skydome - This is a diffuse light generator that mimics the lighting from a skydome light. It does this by taking the direction to each point in the "dome" (a sphere generated based on input) and the mesh surface normal, performing a dot product and multiplying by the light's intensity.
- **VHH::Tool::LB_spot** (`VHH__LightBox__compounds__LB_spot`) — Component Compound - this compound is a light in the the LightBox system. Spotlight - This is a diffuse light generator that mimics the lighting from a spot light. It does this by taking the light direction and the mesh surface normal, performing a dot product and multiplying by the light's intensity. Then applying shadow and penumbra information .

### array (6)
- **VHH::Core::Array::average_array** (`VHH__array__average_array`) — Averages the contents of an array
- **User::Compounds::find_in_string_array, ValHallen::Helpers::find_in_string_array** (`VHH__array__find_in_string_array`)
- **User::Compounds::fit_array, User::Compounds::fit_array** (`VHH__array__fit_array`)
- **VHH::Core::Array::pop_from_array** (`VHH__array__pop_from_array`) — A fast way of removing a value from an array. This compound uses slice array tot pop a value from an array.
- **VHH::Visualize::Display::random_color_array** (`VHH__array__random_color_array`) — generate an array of random colour values.
- **VHH::Core::Array::random_get_from_array** (`VHH__array__random_get_from_array`)

### fields (5)
- **VHH::Core::Fields::adjust_field_in_place, VHH::Core::Fields::adjust_field_in_place** (`VHH__fields__adjust_field_in_place`) — This compound might be better described as fCurve field with magnitude. This allows fCurve adjustment over a 0-1 range without changing the magnitude of the field to match.
- **VHH::Core::Fields::change_range_field** (`VHH__fields__change_range_field`) — Remaps one or more value from one range to another. Returns the result that has the same proportion along the interval between min and max as the input value has between old min and old max. The clamp option limits values that fall outside of the ranges. Works with scalar and vector fields.
- **VHH::Core::Fields::falloff_field** (`VHH__fields__falloff_field`) — Spherical falloff field.
- **VHH::Core::Fields::change_range_field** (`VHH__fields__field_change_range`) — Remaps one or more value from one range to another. Returns the result that has the same proportion along the interval between min and max as the input value has between old min and old max. The clamp option limits values that fall outside of the ranges. Works with scalar and vector fields.
- **VHH::Core::Fields::fit_field_range, VHH::Core::Fields::fit_field_range** (`VHH__fields__fit_field_range`) — This compound fits a field being used for displacement to a user-specified range. It works with both scalar and vector fields. The compound requires a mesh for sampling.

### points (5)
- **VHH::Core::Geometry::points_in_a_circle** (`VHH__points__points_in_a_circle`) — Uniform random points in a circle by radius, count and offset
- **VHH::Core::Geometry::points_in_a_sphere** (`VHH__points__points_in_a_sphere`) — This is basically a "sphrand" compound, with various controls. It uses math to generate points in a sphere uniformly, then gives you some options for rearranging them to your liking.
- **VHH::Core::Geometry::quick_grid** (`VHH__points__quick_grid`) — Quick point grid generator. [ quick grid (youtube) ](https://youtu.be/M8I1YzLDlds)
- **VHH::Core::Geometry::scatter_on_scatter** (`VHH__points__scatter_on_scatter`) — A scattered clustering system based on scatter on points . This allows control by distance and distribution. The compound requires input points, and if a mesh is provided will snap the resulting clusters to the mesh. Without the mesh it will revert to scatter on points behaviour, and scatters spheres.
- **VHH::Core::Geometry::update_cloud_neighbors** (`VHH__points__update_cloud_neighbors`) — Generates point neighbors for a point cloud.

### random (4)
- **VHH::Core::Random::jitter_nova** (`VHH__random__jitter_nova`) — New version of the ancient jitter node. Randomly moves points around on strands, meshes and pointclouds
- **VHH::Core::Random::voronoise** (`VHH__random__voronoise`) — Generates a voronoi pattern based on the surface points on an object by generating a random scattering of feature points and calculating the voronoi diagram.
- **VHH::Core::Random::worley_F1** (`VHH__random__worley_F1`) — Basic Worley (Cellular) Noise Generator. One point per cell, takes the nearest neighbor to calculate distance (n = 1).
- **VHH::Core::Random::worley_F2** (`VHH__random__worley_F2`) — Basic Worley (Cellular) Noise Generator. One point per cell, performs math on two of the nearest neighbors to calculate distance.

### anim (3)
- **VHH::Core::Animation::change_on_frame** (`VHH__anim__change_on_frame`)
- **VHH::Core::Animation::loop_cache** (`VHH__anim__loop_cache`) — Compound takes in a cache file as a .bob or .abc and outputs a seamless loop between start frame and end frame .
- **VHH::Core::Animation::move_points_along_strand** (`VHH__anim__move_points_along_strand`)

### logic (3)
- **VHH::Core::Logic::compare, VHH::Core::Logic::compare, VHH::Core::Logic::compare, VHH::Core::Logic::compare, VHH::Core::Logic::compare, VHH::Core::Logic::compare, VHH::Core::Logic::compare** (`VHH__logic__compare`) — This compound compares two values and returns true or false. It currently supports float, float3, long, double, 4x4, string and int inputs. Note : Comparison is performed member by member. test The comparison operation: equal, less, greater, less or equal, greater or equal, not equal.
- **VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch, VHH::Core::Logic::switch** (`VHH__logic__switch`) — This compound enables the switching between elements in an array. [ switch (youtube) ](https://youtu.be/-p5VFUqGkWc) inputs &nbsp;&nbsp; ■ ■ ■ ■ ■ ■ ■
- **VHH::Core::Logic::weighted_activation** (`VHH__logic__weighted_activation`) — Basically a weighted if, with an option to enable and disable entirely.

### prototypes (1)
- **VHH::Core::Geometry::test_centroid** (`VHH__prototypes__WIP_centroid`)

### tags (1)
- **VHH::Core::Tags::tag_by_string** (`VHH__tags__tag_by_string`) — This compound allows you to select components to tag. The components can be selected by single number, ranges and ranges by step, see description below.

### USD (1)
- **VHH::USD::define_usd_pbr_preview_surface** (`VHH__USD__PBR_Preview_Surface`) — This compound creates a prim that defines a PBR material with a UsdPreviewSurface shader. It allows you to connect textures up to the various inputs that make up the shader. This compound is intended to make and export PBR game shaders and materials to game engines like Unreal or Unity, or systems like Omniverse. It is designed to create a prim definition to be plugged into an existing USD system.

### volume (1)
- **VHH::Volume::volume_density_fade** (`VHH__volume__vol_density_fade`) — Description.
