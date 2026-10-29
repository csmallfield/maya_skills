# Autodesk Bifrost Workflow Corpus

Normalized graphs: **105**

Use `scripts/search_graph_examples.py` for targeted retrieval and `scripts/inspect_graph.py` for a graph summary.

## Categories

### Rigging (16)
- **aim_matrix** — Create a grid of transform matrices and aim them toward the primary and secondary target matrices. Additional weights are generated to scale the aim effect more on the matrices closer to the primary target. Finally, the aimed matrices are converted to instances.
- **arm_module** — An example graph demonstrating how to setup and use the arm module for rigging and animation. The arm module offers features such as IK/FK blend, roll & twist, double hinge support, adaptive scaling, and more.
- **biped_modules** — A template for a biped rig built from and driven by several rigging modules.
- **blend_matrix** — Blend a matrix with multiple blend targets sequentially.
- **compute_transform_chain** — This graphs demonstrates how to use the transform data type to compute transforms as a connected chain rather than as isolated matrices. Consequently, each transform in the sequence inherits movements from its preceding parent transform.
- **dancing_skeleton** — Procedurally construct a skeleton with a spine and arms, compute its animation. Additionally, get the head joint data to drive the motion of the head mesh.
- **elastic_skeleton** — An example graph demonstrating how to use the simulate_rods solver to constrain transforms and stretch a whole biped skeleton.
- **eye_module** — An example graph demonstrating how to use and setup the eye_module to rig the eyes and eyelids of a character.
- **parent_matrix** — Using the "parent_matrix" node, dynamically switch a ball's parenting association between two hands. Offset matrices are computed to ensure a smooth and natural transition as it shifts from one hand to the other.
- **pick_matrix** — Select which transform components from an input matrix to keep.
- **resample_matrix_chain** — Resamples a matrix chain to create interpolated matrices between the input matrices.
- **rope_module** — An example graph demonstrating how to use and setup the rope_module to rig and simulate a rope.
- **skeleton_to_strands** — Using Maya joint data, we show the process of reconstructing a skeleton. This demonstration covers both the creation of a skeleton from the joints' full paths and the subsequent conversion of that skeleton into strands.
- **swinging_coil** — An example graph demonstrating how to use the simulate_rods solver to simulate a transform chain with the shape of a coil realistically.
- **walking_centipede** — Procedurally construct a centipede skeleton with a spine and legs, then compute its animation in two steps. First, solve the spine animation by  driving it from the head and applying inextensibility is applied on it. Then, solve all legs animation by feeding them in an IK solver, and drive the IK target procedurally using a target blending mechanism.
- **wobbling_plant** — An example graph demonstrating how to use the simulate_rods solver to apply secondary animation on a wobbling plant's skeleton.

### Smoke (14)
- **aero_colors** — This graph shows basic handling of an aero color property for colored smoke effects.
- **aero_fields_sourcing** — Using fields to create interesting sources for aero.
- **aero_uvw_field_noise** — Using uvw texture coordinates with fields to apply noise to aero fog density.
- **billowy_smoke_plume** — An aero simulation graph producing a billowy smoke plume
- **cigarette_smoke** — An aero simulation producing cigarette type smoke
- **dry_ice** — An aero simulation graph producing a dry ice effect
- **fast_aero** — An aero simulation tailored for maximum performance
- **ground_mist** — An aero grah producing a ground mist simulation, with adaptivity for low-res pre-roll.
- **post_aero_refinement** — This graph utilizes the post_refine_aero compound to refine an aero volume and add more detail after the simulation.
- **powder_explosion** — This graph simulates an explosion of colored powder, where colored particles emit into an aero simulation.
- **smoke_trail** — An aero simulation producing a smoke trail
- **steamy_breath** — An aero graph producing a steamy breath style simulation
- **vehicle_exhaust** — An aero simulation graph producing a racing vehicle exhaust effect.
- **waterfall_mist** — An MPM fluid simulation sourcing aero to produce mist

### Scatter Pack (9)
- **basic_scatter_example** — Creates an effect of layered instances by scattering with blue noise and then angling the instanced geometries upward so they lay over each other.
- **flocking_solver** — Basic Flocking Solver
- **incircle_packing** — This graph creates a non-intersecting instance setup using the properties of triangles.
- **point_infection** — Simple space colonisation graph
- **scatter_around_strand** — Scatter points around a strand
- **scatter_in_volume** — Simple scatter in volume
- **scatter_on_points** — Scatter points on points
- **scatter_orientations_example** — Demonstrates simply how orientations are generated by scatter_points by instancing some axes onto the scattered points.
- **valley_forest** — Creates a landscape of rolling hills and puts a forest of simple cartoony trees into the valleys of that landscape.

### Rigid Body (8)
- **constrain_by_tag** — An example of named rigid bodies, constraining and shading by component tag.
- **glass_shatter** — This graph uses complex fracturing techniques to achieve a shattered glass effect.
- **glue_constraints** — This graph demonstrates glue constraint and control.
- **multi_constraints** — This graph showcases four RBD constraints:  hinge, slider, spring and cone-twist.
- **rigid_body_instances** — This graph demontrates rigid body instances
- **scatter_and_settle** — This graph demostrates using RBD to scatter and settle instances.
- **scatter_and_settle_instant** — This graph demonstrates the use of the RBD solver as pre-roll.
- **simple_RBD** — A simple RBD stack example

### Fire (7)
- **burning_barrel** — An aero combustion simulation creating a burning barrel effect
- **flame_torch** — This graph uses Aero to produce a torch-style flame
- **large_turbulent_fire** — This graph illustrates how to set up a large-scale simulation of turbulent flames using Aero and how to render it with high detail using a shader network in Arnold.
- **mega_explosion** — An extensive graph which uses particles and multiple fuel sources to produce a big cascading blast with flaming projectile debris
- **missile_hit** — An exploding missile trail aero simulation with debris
- **pyroclastic_explosion** — This graph shows how to use Bifrost Aero to create a large, pyroclastic explosion.
- **standard_explosion** — A aero and combustion graph producing a standard explosion

### Liquid (7)
- **dam_break_foam** — This graph takes the same setup as in the previous graph (dam_break_particles), meshes it and adds foam to the final result.
- **dam_break_particles** — Very basic dam break liquid example.  This graph is nothing but setting up and simulating the fluid particles.
- **guided_liquid** — This graph demonstrates a liquid sim informed and guided by a spectral ocean.
- **liquid_meshing** — A graph that meshes fluid particle simulations
- **procedural_stream** — This graph showcases the procedural generation of a stream
- **surface_tension_explicit** — This graph demonstrates a classic crown splash using an explicit surface tension solver.
- **surface_tension_implicit** — This graph showcases a droplet collision using an implicit surface tension solver.

### Particles (6)
- **confetti_pop** — Combines aero and particle systems to create a confetti-popping-out-of-a-bottle effect
- **dust_motes** — The purpose of this graph is to show how to use Bifrost particles and instancing to simulate dust motes in the air
- **fiber_dust_motes** — Creates floating dust motes as a particle system, generates variations of fibers, and instances them.
- **fireworks** — This graph utilizes the filter_particles node to provide controlled spawning between particle simulation systems and produce a fireworks effect.
- **gradient_advection** — Particle advection by volume gradient
- **random_particle_rotations** — Demonstrates how to source and randomize particle orientation and spin

### Fracture (4)
- **boolean_fracture** — This graph shows a boolean_fracture example
- **edge_damage_intersection** — A demonstration of edge damage by intersection method
- **edge_damage_slice** — A demonstration of edge damage by boolean slice method
- **voronoi_fracture** — This graph shows a voronoi_fracture example

### Geometry Queries (4)
- **basic_raycast_example** — A simple raytracing example which creates a spinning sphere and raycasts from all the normals to a terrain.
- **sample_points_by_radius** — This example demonstrates weighted sampling between points and a plane
- **snow_shadows** — Puts gloopy melting snow on top of surfaces but not under them (leaving a "snow shadow"). Uses scattering, ray-casting, and meshing of volumes.
- **test_inside_mesh_example** — A sample which tests two meshes to see if any points of either mesh are inside the other.  To do this, it uses a closest_location lookup to see if it finds a rear-facing normal or not.

### Ocean (4)
- **dynamic_boat_wake** — A procedural ocean surface with simulated wake and foam.
- **dynamic_raindrops** — A graph that demonstrates simulating raindrops with two different methods.
- **ocean_wave_with_spray** — An ocean with waves and spray
- **view_based_ocean** — An ocean mesh that is fit to the camera view, more polygons close to the camera, less on the horizon.

### Snow (3)
- **snow_activation** — MPM snow simulation that shows dynamic activation of points using an infection solver
- **snow_aero** — A snowball breaks apart on a wedge
- **snowball_throw** — An MPM simulation of a snowball being thrown against a wall

### Texture (3)
- **bake_texture**
- **read_texture** — A texture is made of one or more images, in a texture-atlas (such as "UDIM") space.  This graph illustrates the reading of a file from disk.
- **texture_scatter** — This graph illustrates the use of read_texture to drive a scatter density and output color.

### Fields (2)
- **boiling_noise** — A boiling effect is created by repeatedly displacing a mesh. This causes bulges to bulge out further and animated the noise creates a boiling effect.
- **flat_hurricane_noise** — Creates a flow field where the flow spirals inward toward "attractors" by manipulating noise fields, gradients, and other basic vector operations. Then visualizes the fields with flowlines.

### Gel (2)
- **gel_checker** — A gel torus with checkboard material smashes into the ground
- **ice_cream** — Soft serve icecream is dispensed into a waffle cone

### Machine Learning (2)
- **generate_data** — This graph generates the transform data for the FK to IK Machine Learning Example
- **neural_network** — This graph interprets the trained data from the generate_data browser graph

### Rubber (2)
- **MPM_rubber** — Wrap deform a polygon mesh with moving points from an MPM Rubber simulation.
- **rubber_helix** — MPM rubber scene that shows surfacing workflow

### Sand (2)
- **sand_grain_instances** — MPM sand scene that shows instancing workflow
- **sand_pile** — A very simple grains simulation, in the form of a pile of sand.

### Shell (2)
- **plastic_deformation** — This graph utilizes the make_mpm_shell source to create a plastic deformation simulation.
- **twist_rainbow_shell** — An MPM simulation of shell twisting from constraints

### Strands (2)
- **embroidery** — A strands example illustrating how strands can be used to make an embroidery-type effect
- **grass_wind** — This graph generates a field of grass, waving in the wind

### Tags (2)
- **flowers** — This graph uses tagging nodes to generate a field of flowers.
- **procedural_gear** — Create a procedural gear using component tags

### Volumes (2)
- **muzzle_flash** — This graph shows how to combine custom mesh deformation and volume tools to create an animated muzzle-flash.
- **ragged_cloud** — This graph provides an easy way to turn arbitrary meshes into a cloud-like volume.  Volumes can also be cached to disk as .vdb files.

### Cloth (1)
- **tearing_cloth** — An MPM simulation of cloth tearing through constraints

### Wedging (1)
- **aero_combustion_wedging** — This graph demonstrates the wedging service
