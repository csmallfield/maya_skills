# Installed compound compatibility with Bifrost 3.0

Folder: C:\Users\smallfch\Autodesk\Bifrost\Compounds

Bifrost 3.0.0.0, compiled by name with bifcmd (2026-10-29). 5 auto inputs (needs a graph), 16 compiles, 1 fails.

| Compound | File | Status | Detail |
|---|---|---|---|
| `CityGen::Restart::cg_flat_layout_v001` | cg_flat_layout_v001.json | fails | no promotion exists from a value of type 'float' to a value of type 'array<float>'; no promotion exists from a value of type 'float' to a value of type 'array<float>'; no promotion exists from a value of type 'float' to a value of type 'array<Math::float3>' |
| `CityGen::Roads::citygen_road_topology_v0_1` | citygen_road_topology_v0_1.json | compiles |  |
| `User::Compounds::CJS_genRock` | CJS_genRock.json | auto inputs (needs a graph) | you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port. |
| `User::Compounds::CJS_makeProxy` | CJS_makeProxy.json | auto inputs (needs a graph) | you must explicitly set the type of this compound input port. |
| `User::Compounds::CJS_points_to_USD_points` | CJS_points_to_USD_points.json | compiles |  |
| `User::Compounds::CJS_simple_usd_loader` | CJS_simple_usd_loader.json | compiles |  |
| `User::Compounds::CJS_usd_scatter` | CJS_usd_scatter.json | auto inputs (needs a graph) | you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port. |
| `FX::Goo::cs_green_goo_v3` | cs_green_goo_v3.json | compiles |  |
| `FX::Goo::cs_green_goo_v4` | cs_green_goo_v4.json | compiles |  |
| `FX::Goo::cs_green_goo_v5` | cs_green_goo_v5.json | compiles |  |
| `FX::Fire::cs_mesh_fire` | cs_mesh_fire.json | compiles |  |
| `Bifrost_workshop::Compounds::descend` | descend.json | auto inputs (needs a graph) | you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound input port. |
| `User::Compounds::GL_replace_point_instancer_prototype` | GL_replace_point_instancer_prototype.json | compiles |  |
| `User::Compounds::GL_usd_point_instancer_scope` | GL_usd_point_instancer_scope.json | auto inputs (needs a graph) | you must explicitly set the type of this compound input port.; you must explicitly set the type of this compound output port.; you must explicitly set the type of this compound output port. |
| `Procedural::Buildings::ppg_nyc_skyscraper_v3_1_fast` | ppg_nyc_skyscraper_v3_1_fast.json | compiles |  |
| `Procedural::Buildings::ppg_urban_mesh_bake_v3` | ppg_urban_mesh_bake_v3.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v2` | ppg_urban_multistyle_v2.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v3` | ppg_urban_multistyle_v3.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v4` | ppg_urban_multistyle_v4.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v4_1` | ppg_urban_multistyle_v4_1.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v4_2` | ppg_urban_multistyle_v4_2.json | compiles |  |
| `Procedural::Buildings::ppg_urban_multistyle_v4_3` | ppg_urban_multistyle_v4_3.json | compiles |  |

## Reading this

- **compiles**: loads and compiles on 3.0 with bifcmd, with the USD pack loaded from MayaUSD's libraries. Not executed; use `verify_compound.py` for that.
- **auto inputs (needs a graph)**: bifcmd can't compile a compound with untyped inputs (or outputs) on its own. In Maya the connected ports give them types, so this is not a 3.0 failure. Check one inside a headless graph with real inputs before relying on it.
- **fails**: real compile errors. `cg_flat_layout_v001` has values on multi-input ports (regression-history.md, Case E). The fixed `cg_flat_layout_v002` is in the repo's `work/` folder, VERIFIED, and not installed.

Regenerate with `python -I scripts/scan_compounds.py --out references/installed-compounds-3.0.md`; that writes the table only.
