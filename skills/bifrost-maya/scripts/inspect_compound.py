#!/usr/bin/env python3
import argparse, json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / 'references' / 'compound-data'


def find_id(query):
    direct = DATA / 'normalized' / f'{query}.json'
    if direct.exists(): return direct
    idx = json.loads((DATA / 'compound-index.json').read_text(encoding='utf-8'))
    q = query.lower()
    matches = [r for r in idx if q == r['id'].lower() or any(q == (n or '').lower() for n in r.get('root_names', []))]
    if not matches:
        matches = [r for r in idx if q in r['id'].lower() or any(q in (n or '').lower() for n in r.get('root_names', []))]
    if len(matches) == 1:
        return DATA / 'normalized' / f"{matches[0]['id']}.json"
    if not matches:
        raise SystemExit(f'No compound matching: {query}')
    raise SystemExit('Ambiguous: ' + ', '.join(r['id'] for r in matches[:20]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('compound')
    ap.add_argument('--connections', type=int, default=30)
    args = ap.parse_args()
    p = find_id(args.compound)
    rec = json.loads(p.read_text(encoding='utf-8'))
    print(f"ID: {rec['id']}")
    print(f"Source: {rec['source_path']}")
    print(f"Collection/category: {rec['collection']} / {rec['category']}")
    print(f"Counts: {rec['counts']}")
    for root in rec['roots']:
        print('\n' + '='*72)
        print(f"Compound: {root.get('name')}  overload={root.get('overload_index')}  default={root.get('is_default_overload')}")
        if root.get('documentation_file'): print('Documentation:', root['documentation_file'])
        if root.get('documentation'):
            print('\nDocumentation excerpt:')
            print(root['documentation'][:1800].strip())
        print('\nPorts:')
        for port in root.get('ports', []):
            default = f" default={port['default']}" if 'default' in port else ''
            print(f"  {port.get('direction','?'):6} {port.get('name')} : {port.get('type')}{default}")
        if root.get('custom_dependencies'):
            print('\nCustom dependencies:')
            for n,c in sorted(root['custom_dependencies'].items(), key=lambda kv:(-kv[1],kv[0])):
                print(f'  {n} x{c}')
        print('\nMost-used node types:')
        for n,c in list(root.get('node_types', {}).items())[:30]: print(f'  {n} x{c}')
        print('\nRepresentative connections:')
        for c in root.get('connections', [])[:args.connections]:
            print(f"  [{c.get('path')}] {c.get('source')} -> {c.get('target')}")
        notes=[]
        for nc in root.get('nested_compounds', []):
            md=nc.get('metadata') or {}
            notes.extend(md.get('_notes',[]) or [])
        if notes:
            print('\nTeaching/sticky notes:')
            for n in notes[:20]: print('  -', n.get('title') or n.get('text'))

if __name__ == '__main__': main()
