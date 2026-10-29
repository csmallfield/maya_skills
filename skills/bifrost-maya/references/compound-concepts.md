# Custom compound corpus: PPG, VHH, and related libraries

Use this reference when a task involves the user-provided compound library rather than only Autodesk built-in nodes.

## Source status

The compound corpus is user-provided and is separate from the Autodesk/Maya-shipped example corpus. Treat it as direct evidence of the supplied compound implementations and documentation, not as Autodesk documentation unless a node used internally is covered by the bundled Autodesk node reference.

The normalized corpus contains 229 compound-bearing JSON files from 238 JSON files total, plus 8 VHH enum/type definition files. The largest collections are VHH and PPG 2.80 beta1. PPG 2.80 is the version installed in the user's Maya; it replaced Astra's PPG 2.0 copy, and `references/ppg-2.0-vs-2.80.md` lists what changed.

## Retrieval workflow

1. Search by artistic intent, compound name, port name, internal node type, or dependency with `scripts/search_compounds.py`.
2. Inspect the strongest match with `scripts/inspect_compound.py` before asserting an exact custom-compound interface.
3. Use `references/compound-data/interface-index.json` when exact input/output names and types matter across overloads.
4. Use `references/compound-data/name-index.json` to resolve names to files and overloads.
5. Use `references/compound-data/dependency-index.json` to trace compound-to-compound dependencies.
6. Use `references/compound-data/type-definitions.json` for bundled VHH enum definitions.
7. If a dependency appears in `unresolved-dependencies.json`, treat it as external or otherwise absent from this corpus and do not invent its implementation.

## PPG 2.80 beta1

PPG compounds use the `PPG::` namespace for the main polygon-procedural toolkit, with supporting compounds in additional namespaces where supplied by the source collection.

The corpus is strongly oriented around polygon face workflows: face IDs and tags, face/edge selection, patterned cuts, extrusion-style modeling, transforms, instancing, material assignment, and pattern generation. The PPG documentation frequently describes artist-facing controls and expected selection behavior, so prefer the bundled documentation text over inferring semantics from the internal graph alone.

For a PPG task:

- Browse `references/compound-data/ppg-overview.md` when the needed compound is not yet known.
- Search the corpus for the user's operation and relevant selection language.
- Inspect the exact PPG compound to recover the documented controls, exact ports, and supporting-compound dependencies.
- Trace face/tag conventions through the compound rather than substituting a generic Bifrost selection approach unless explicitly redesigning the tool.
- Preserve PPG namespace and compound names exactly when giving implementation instructions.

For procedural buildings, facade repetition or PPG performance, read `ppg-building-design.md` and use `ppg-documentation-index.md` for the supplied written documentation. Resolve numeric modes and output representation from exact implementations, not names or prose order.

## VHH

VHH is a broad compound library rather than one single tool family. The supplied corpus includes geometry, tools, fields, math, display helpers, points, arrays, animation, logic, randomization, LightBox-related compounds, USD helpers, tags, volumes, and custom enums.

Important VHH patterns include overloaded compounds and ecosystem-style tools whose supporting compounds are intended to work together. The `displacer` family is one example: documentation and dependencies should be inspected together instead of treating a single node in isolation.

For a VHH task:

- Browse `references/compound-data/vhh-overview.md` for the family/category.
- Search by intent plus likely terms such as property, field, scatter, strand, display, blur, road, displacement, array, or USD.
- Inspect exact overloads and port signatures before wiring a VHH compound.
- Preserve custom enum types and values when they appear in an interface; verify them through `type-definitions.json`.
- Follow documented ecosystem relationships and dependencies rather than replacing them with superficially similar built-in nodes unless the user asks for a rewrite.

## Overloads and interfaces

Several VHH files contain multiple overloads with the same compound name. Do not collapse these into one guessed signature. Select the overload by the actual port types and the `is_default_overload` marker when present.

A missing or `None` port type in the source is not permission to invent a type. Report the source as auto/unspecified and infer only when the connected topology makes the inference useful, labeling it as inference.

## Internal topology versus public interface

For normal usage, prefer the public compound interface and its documentation. Inspect internal topology when:

- troubleshooting a compound;
- explaining why a control behaves a certain way;
- adapting or extending the implementation;
- resolving property, field, array, or type flow;
- identifying a dependency or performance bottleneck;
- recreating behavior without the compound installed.

When recreating a custom compound from internals, distinguish exact source-derived connections from any redesign decisions.
