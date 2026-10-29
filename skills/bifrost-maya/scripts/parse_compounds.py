#!/usr/bin/env python3
"""Normalize third-party/user Bifrost compound libraries for skill retrieval.

The source format is Autodesk Bifrost compound JSON. The normalizer removes UI-only
layout metadata while retaining compound interfaces, nested topology, authored values,
documentation, enum/type definitions, and custom-compound dependencies.
"""
import argparse
import collections
import json
import pathlib
import re

DROP_META = {
    'LayoutPos', 'zValue', 'ViewportRect', 'DisplayMode', 'PortExpandedState',
    'coords', 'color', 'fontSize', 'format', 'thumbnail', '_recentNode_',
    'NodeWidthOffset', 'NodeValueDisplay', 'UILayout', 'icon',
}
KEEP_META = {
    'author', 'category', 'description', 'documentation', 'compoundIsGraph',
    'type', 'title', 'text', 'uiName', 'niceName', 'help', 'tooltip',
}
BUILTIN_PREFIXES = (
    'Core::', 'Geometry::', 'Modeling::', 'Simulation::', 'Rendering::',
    'File::', 'Diagnostic::', 'Rigging::', 'Machine_Learning::', 'Scatter::',
)


def slug(text):
    text = re.sub(r'[^A-Za-z0-9._-]+', '_', text.strip())
    return text.strip('_') or 'compound'


def simplify_metadata(items):
    out = {}
    notes = []
    sections = []
    for item in items or []:
        name = item.get('metaName')
        if name in DROP_META:
            continue
        if 'metadata' in item:
            nested = simplify_metadata(item.get('metadata') or [])
            rec = {k: nested.get(k) for k in ('type', 'title', 'text') if nested.get(k)}
            if rec:
                typv = rec.get('type') or ''
                if isinstance(typv, list):
                    typ = ' '.join(str(x) for x in typv).lower()
                else:
                    typ = str(typv).lower()
                if 'sticky_note' in typ or rec.get('text'):
                    notes.append(rec)
                elif rec.get('title'):
                    sections.append(rec)
            continue
        if name in KEEP_META and 'metaValue' in item:
            val = item.get('metaValue')
            if name in out:
                if not isinstance(out[name], list):
                    out[name] = [out[name]]
                out[name].append(val)
            else:
                out[name] = val
    if notes:
        out['_notes'] = notes
    if sections:
        out['_sections'] = sections
    return out


def simplify_ports(ports):
    out = []
    for p in ports or []:
        rec = {
            'name': p.get('portName'),
            'direction': p.get('portDirection'),
            'type': p.get('portType'),
        }
        default = p.get('portDefault', None)
        if default not in (None, {}, [], ''):
            rec['default'] = default
        md = simplify_metadata(p.get('metadata') or [])
        if md:
            rec['metadata'] = md
        out.append(rec)
    return out


def simplify_value(v):
    rec = {'name': v.get('valueName'), 'type': v.get('valueType')}
    value = v.get('value', None)
    if value not in (None, {}, []):
        rec['value'] = value
    return rec


def resolve_doc(json_path, doc_ref, library_root):
    if not doc_ref:
        return None, None
    candidates = []
    p = (json_path.parent / doc_ref).resolve()
    candidates.append(p)
    basename = pathlib.Path(doc_ref).name
    if basename:
        candidates.extend(library_root.rglob(basename))
    seen = set()
    for c in candidates:
        key = str(c)
        if key in seen:
            continue
        seen.add(key)
        if c.is_file():
            try:
                text = c.read_text(encoding='utf-8', errors='replace').strip()
            except Exception:
                text = ''
            try:
                rel = str(c.relative_to(library_root)).replace('\\', '/')
            except ValueError:
                rel = c.name
            return rel, text
    return doc_ref, None


def root_doc_ref(comp):
    for m in comp.get('metadata', []) or []:
        if m.get('metaName') == 'documentation':
            return m.get('metaValue')
    return None


def normalize_nested(comp, path='root', nodes=None, conns=None, vals=None, nested=None):
    if nodes is None:
        nodes, conns, vals, nested = [], [], [], []
    meta = simplify_metadata(comp.get('metadata') or [])
    local_nodes = []
    for n in comp.get('compoundNodes', []) or []:
        rec = {
            'path': path,
            'name': n.get('nodeName'),
            'type': n.get('nodeType') or 'Unknown',
        }
        if n.get('fanInPortNames'):
            rec['fan_in_ports'] = n.get('fanInPortNames')
        if n.get('terminalStates'):
            rec['terminal_states'] = n.get('terminalStates')
        nm = simplify_metadata(n.get('metadata') or [])
        if nm:
            rec['metadata'] = nm
        nodes.append(rec)
        local_nodes.append(rec)
    for c in comp.get('connections', []) or []:
        conns.append({'path': path, 'source': c.get('source'), 'target': c.get('target')})
    for v in comp.get('values', []) or []:
        rec = simplify_value(v)
        rec['path'] = path
        vals.append(rec)
    nested.append({
        'path': path,
        'name': comp.get('name'),
        'metadata': meta,
        'ports': simplify_ports(comp.get('ports') or []),
        'terminal_states': comp.get('terminalStates') or [],
        'counts': {
            'nodes': len(local_nodes),
            'connections': len(comp.get('connections') or []),
            'values': len(comp.get('values') or []),
            'children': len(comp.get('compounds') or []),
        },
    })
    for i, child in enumerate(comp.get('compounds', []) or []):
        cname = child.get('name') or f'compound_{i}'
        normalize_nested(child, f'{path}/{slug(cname)}', nodes, conns, vals, nested)
    return nodes, conns, vals, nested


def normalize_root(comp, idx, json_path, library_root, known_compounds):
    nodes, conns, vals, nested = normalize_nested(comp)
    node_counts = collections.Counter(n['type'] for n in nodes)
    doc_ref = root_doc_ref(comp)
    doc_file, doc_text = resolve_doc(json_path, doc_ref, library_root)
    deps = collections.Counter()
    for typ, count in node_counts.items():
        if typ in known_compounds:
            deps[typ] += count
        elif typ and '::' in typ and not typ.startswith(BUILTIN_PREFIXES):
            deps[typ] += count
    return {
        'overload_index': idx,
        'name': comp.get('name'),
        'uri_imported': comp.get('uriImported'),
        'is_default_overload': comp.get('isDefaultOverload'),
        'metadata': simplify_metadata(comp.get('metadata') or []),
        'documentation_file': doc_file,
        'documentation': doc_text,
        'ports': simplify_ports(comp.get('ports') or []),
        'terminal_states': comp.get('terminalStates') or [],
        'counts': {
            'nodes': len(nodes),
            'connections': len(conns),
            'values': len(vals),
            'nested_compounds': len(nested),
        },
        'node_types': dict(node_counts.most_common()),
        'custom_dependencies': dict(deps.most_common()),
        'nodes': nodes,
        'connections': conns,
        'values': vals,
        'nested_compounds': nested,
    }


def classify_path(rel):
    parts = rel.parts
    collection = parts[0] if parts else 'root'
    parent = '/'.join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) == 2 else '')
    if not parent:
        parent = 'root'
    return collection, parent


def gather_known_names(files):
    names = set()
    for p in files:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            continue
        for c in d.get('compounds', []) or []:
            if c.get('name'):
                names.add(c['name'])
    return names


def type_defs(d):
    out = []
    for t in d.get('types', []) or []:
        if 'enumName' in t:
            out.append({
                'kind': 'enum',
                'name': t.get('enumName'),
                'members': [
                    {'key': m.get('enumKey'), 'value': m.get('enumValue')}
                    for m in t.get('enumMembers', []) or []
                ],
            })
        else:
            out.append(t)
    return out


def clean_text(text):
    if not text:
        return ''
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    text = re.sub(r'<br\s*/?>', ' ', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[#*_`]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def first_paragraph(text):
    if not text:
        return ''
    text = re.sub(r'```.*?```', ' ', text, flags=re.S)
    lines = [x.strip() for x in text.splitlines()]
    buf = []
    for line in lines:
        if not line:
            if buf:
                break
            continue
        if line.startswith('#'):
            continue
        buf.append(line)
        if len(' '.join(buf)) > 360:
            break
    return clean_text(' '.join(buf))[:500]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', type=pathlib.Path)
    ap.add_argument('out', type=pathlib.Path)
    args = ap.parse_args()
    src = args.source.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    norm = out / 'normalized'
    norm.mkdir(exist_ok=True)

    files = sorted(src.rglob('*.json'))
    known = gather_known_names(files)
    records = []
    errors = []
    enum_defs = []

    for p in files:
        rel = p.relative_to(src)
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e:
            errors.append({'path': str(rel), 'error': str(e)})
            continue
        defs = type_defs(d)
        if defs:
            enum_defs.extend({'source_path': str(rel).replace('\\', '/'), **x} for x in defs)
        roots = d.get('compounds', []) or []
        if not roots:
            continue
        collection, category = classify_path(rel)
        fid = slug('__'.join(rel.with_suffix('').parts))
        normalized_roots = [normalize_root(c, i, p, src, known) for i, c in enumerate(roots)]
        docs = [r.get('documentation') for r in normalized_roots if r.get('documentation')]
        total = {
            'nodes': sum(r['counts']['nodes'] for r in normalized_roots),
            'connections': sum(r['counts']['connections'] for r in normalized_roots),
            'values': sum(r['counts']['values'] for r in normalized_roots),
            'overloads': len(normalized_roots),
        }
        port_names = sorted({p.get('name') for r in normalized_roots for p in r.get('ports', []) if p.get('name')})
        node_types = sorted({n for r in normalized_roots for n in r.get('node_types', {}) if n})
        dependencies = sorted({n for r in normalized_roots for n in r.get('custom_dependencies', {}) if n})
        rec = {
            'id': fid,
            'collection': collection,
            'category': category,
            'source_path': str(rel).replace('\\', '/'),
            'root_names': [r.get('name') for r in normalized_roots],
            'counts': total,
            'documentation_summary': first_paragraph(docs[0]) if docs else '',
            'documentation_search': clean_text(docs[0])[:5000] if docs else '',
            'port_names': port_names,
            'node_types_search': node_types,
            'dependencies_search': dependencies,
            'roots': normalized_roots,
        }
        records.append(rec)
        (norm / f'{fid}.json').write_text(
            json.dumps(rec, ensure_ascii=False, separators=(',', ':')), encoding='utf-8'
        )

    by_collection = collections.defaultdict(lambda: collections.defaultdict(list))
    by_name = collections.defaultdict(list)
    node_usage = collections.defaultdict(list)
    dependency = collections.defaultdict(list)
    interface = collections.defaultdict(list)
    for rec in records:
        by_collection[rec['collection']][rec['category']].append(rec['id'])
        for root in rec['roots']:
            name = root.get('name') or rec['id']
            by_name[name].append({'id': rec['id'], 'overload': root['overload_index'], 'collection': rec['collection']})
            interface[name].append({
                'id': rec['id'],
                'overload': root['overload_index'],
                'is_default_overload': root.get('is_default_overload'),
                'ports': root.get('ports') or [],
            })
            for nt, count in root.get('node_types', {}).items():
                node_usage[nt].append({'id': rec['id'], 'compound': name, 'count': count, 'collection': rec['collection']})
            for dep, count in root.get('custom_dependencies', {}).items():
                dependency[dep].append({'id': rec['id'], 'compound': name, 'count': count, 'collection': rec['collection']})

    index = []
    for rec in records:
        index.append({k: rec[k] for k in ('id', 'collection', 'category', 'source_path', 'root_names', 'counts', 'documentation_summary', 'documentation_search', 'port_names', 'node_types_search', 'dependencies_search')})
    (out / 'compound-index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'collection-index.json').write_text(json.dumps(by_collection, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'name-index.json').write_text(json.dumps(by_name, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'interface-index.json').write_text(json.dumps(interface, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'node-usage-index.json').write_text(json.dumps(node_usage, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'dependency-index.json').write_text(json.dumps(dependency, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    unresolved = {k: v for k, v in dependency.items() if k not in known}
    (out / 'unresolved-dependencies.json').write_text(json.dumps(unresolved, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'type-definitions.json').write_text(json.dumps(enum_defs, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
    (out / 'parse-errors.json').write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding='utf-8')

    # Human-readable overview emphasizing PPG and VHH.
    lines = [
        '# Bifrost Compound Library Corpus', '',
        f'Normalized compound files: **{len(records)}**',
        f'Type/enum definition records: **{len(enum_defs)}**', '',
        'Use `scripts/search_compounds.py` for retrieval and `scripts/inspect_compound.py` for exact interfaces/topology.', '',
        '## Collections', ''
    ]
    for collection, cats in sorted(by_collection.items(), key=lambda kv: (-sum(len(v) for v in kv[1].values()), kv[0].lower())):
        total = sum(len(v) for v in cats.values())
        lines.append(f'### {collection} ({total})')
        for cat, ids in sorted(cats.items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
            lines.append(f'- `{cat}` — {len(ids)} files')
        lines.append('')
    (out / 'compound-index.md').write_text('\n'.join(lines), encoding='utf-8')

    def make_focus(collection, title):
        lines = [f'# {title}', '', f'Normalized files: **{sum(len(v) for v in by_collection.get(collection, {}).values())}**', '']
        lines += ['## Categories', '']
        for cat, ids in sorted(by_collection.get(collection, {}).items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
            lines.append(f'### {cat} ({len(ids)})')
            for cid in sorted(ids):
                rec = next(r for r in records if r['id'] == cid)
                roots = ', '.join(x for x in rec['root_names'] if x)
                desc = rec.get('documentation_summary') or ''
                line = f'- **{roots or cid}** (`{cid}`)'
                if desc:
                    line += f' — {desc}'
                lines.append(line)
            lines.append('')
        return '\n'.join(lines)

    (out / 'ppg-overview.md').write_text(make_focus('PPG_V2.0', 'PPG 2.0 Compound Reference'), encoding='utf-8')
    (out / 'vhh-overview.md').write_text(make_focus('VHH', 'VHH Compound Reference'), encoding='utf-8')

    print(f'Normalized {len(records)} compound files from {len(files)} JSON files.')
    print(f'Type/enum definitions: {len(enum_defs)}; errors: {len(errors)}')

if __name__ == '__main__':
    main()
