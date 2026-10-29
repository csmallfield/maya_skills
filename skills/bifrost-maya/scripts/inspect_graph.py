#!/usr/bin/env python3
import argparse,json,pathlib,collections

def main():
    ap=argparse.ArgumentParser(description='Print a compact summary of a normalized Bifrost graph.')
    ap.add_argument('graph_id')
    ap.add_argument('--data',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]/'references'/'workflow-data')
    ap.add_argument('--connections',type=int,default=25)
    args=ap.parse_args(); p=args.data/'normalized'/f'{args.graph_id}.json'
    if not p.exists(): raise SystemExit(f'Graph not found: {args.graph_id}')
    g=json.loads(p.read_text(encoding='utf-8'))
    print(f"# {g['id']}\nCategory: {g.get('category')}\nDescription: {g.get('description') or ''}\nCounts: {g.get('counts')}\nLibraries: {g.get('library_dependencies')}\n")
    if g.get('documentation'): print('## Autodesk explanation\n'+g['documentation'][:5000]+'\n')
    print('## Most-used node types')
    for n,c in list(g.get('node_types',{}).items())[:30]: print(f'- {n}: {c}')
    print('\n## Representative connections')
    for c in g.get('connections',[])[:args.connections]: print(f"- [{c['path']}] {c['source']} -> {c['target']}")
    if g.get('teaching_notes'):
        print('\n## Teaching notes')
        for n in g['teaching_notes'][:12]:
            if n.get('title'): print(f"### {n['title']}")
            print((n.get('text') or '').strip())

if __name__=='__main__': main()
