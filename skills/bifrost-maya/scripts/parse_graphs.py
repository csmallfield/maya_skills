#!/usr/bin/env python3
import argparse, json, pathlib, re, collections

DROP_META = {'LayoutPos','zValue','ViewportRect','DisplayMode','PortExpandedState','coords','color','fontSize','format','thumbnail','_recentNode_'}
KEEP_META = {'author','category','description','documentation','compoundIsGraph','type','title','text'}

def meta_to_dict(items):
    out = {}
    notes=[]
    backdrops=[]
    for item in items or []:
        name=item.get('metaName')
        if 'metadata' in item:
            nested=meta_to_dict(item.get('metadata'))
            if nested.get('text') or nested.get('title'):
                rec={k:v for k,v in nested.items() if k in ('title','type','text') and v}
                if rec:
                    (notes if rec.get('type')=='sticky_note' or rec.get('text') else backdrops).append(rec)
            continue
        if name in DROP_META:
            continue
        if name in KEEP_META and 'metaValue' in item:
            val=item.get('metaValue')
            if name in out:
                if not isinstance(out[name], list): out[name]=[out[name]]
                out[name].append(val)
            else:
                out[name]=val
    if notes: out['_notes']=notes
    if backdrops: out['_backdrops']=backdrops
    return out

def leaf_type(node):
    return node.get('nodeType') or (f"Value::{node.get('valueType')}" if node.get('valueType') else 'Unknown')

def normalize_compound(comp, path='root', all_nodes=None, all_conns=None, all_values=None, compounds=None):
    if all_nodes is None:
        all_nodes=[]; all_conns=[]; all_values=[]; compounds=[]
    meta=meta_to_dict(comp.get('metadata',[]))
    local_nodes=[]
    for n in comp.get('compoundNodes',[]) or []:
        rec={'path':path,'name':n.get('nodeName'),'type':leaf_type(n)}
        nm=meta_to_dict(n.get('metadata',[]))
        if nm: rec['metadata']=nm
        if n.get('fanInPortNames'): rec['fan_in_ports']=n['fanInPortNames']
        if n.get('terminalStates'): rec['terminal_states']=n['terminalStates']
        local_nodes.append(rec); all_nodes.append(rec)
    for c in comp.get('connections',[]) or []:
        rec={'path':path,'source':c.get('source'),'target':c.get('target')}
        local_conns=all_conns; local_conns.append(rec)
    for v in comp.get('values',[]) or []:
        rec={'path':path,'name':v.get('valueName'),'type':v.get('valueType'),'value':v.get('value')}
        all_values.append(rec)
    crec={
        'path':path,
        'name':comp.get('name'),
        'metadata':meta,
        'ports':comp.get('ports',[]) or [],
        'terminal_states':comp.get('terminalStates',[]) or [],
        'node_count':len(local_nodes),
        'connection_count':len(comp.get('connections',[]) or []),
        'value_count':len(comp.get('values',[]) or []),
    }
    compounds.append(crec)
    for i,child in enumerate(comp.get('compounds',[]) or []):
        cname=child.get('name') or f'compound_{i}'
        safe=re.sub(r'[^A-Za-z0-9_.:-]+','_',cname)
        normalize_compound(child, f'{path}/{safe}', all_nodes, all_conns, all_values, compounds)
    return all_nodes, all_conns, all_values, compounds

def read_doc(graph_json):
    parent=graph_json.parent
    candidates=sorted(parent.glob('*_docs_ENU.md'))
    if not candidates: return None, None
    p=candidates[0]
    try: text=p.read_text(encoding='utf-8', errors='replace').strip()
    except Exception: text=''
    return p.name, text

def top_metadata(rootcomp):
    return meta_to_dict(rootcomp.get('metadata',[]))

def normalize_graph(p, base):
    d=json.loads(p.read_text(encoding='utf-8'))
    roots=d.get('compounds',[]) or []
    if not roots: return None
    root=roots[0]
    nodes, conns, vals, comps=normalize_compound(root)
    md=top_metadata(root)
    doc_name,doc_text=read_doc(p)
    type_counts=collections.Counter(n['type'] for n in nodes)
    edge_pairs=collections.Counter()
    for c in conns:
        s=c.get('source') or ''; t=c.get('target') or ''
        sn=s.split('.',1)[0]; tn=t.split('.',1)[0]
        # local instance->type mapping only by matching path
        byname={(n['path'],n['name']):n['type'] for n in nodes}
        st=byname.get((c['path'],sn), sn)
        tt=byname.get((c['path'],tn), tn)
        edge_pairs[f'{st} -> {tt}'] += 1
    notes=[]
    for co in comps:
        mm=co.get('metadata') or {}
        notes.extend(mm.get('_notes',[]) or [])
    return {
        'id':p.stem,
        'compound_name':root.get('name'),
        'source_path':str(p.relative_to(base)).replace('\\','/'),
        'category':md.get('category') or 'Uncategorized',
        'author':md.get('author'),
        'description':md.get('description'),
        'documentation_file':doc_name or md.get('documentation'),
        'documentation':doc_text,
        'library_dependencies':root.get('libraryDependencies',{}) or {},
        'graph_ports':root.get('ports',[]) or [],
        'terminal_states':root.get('terminalStates',[]) or [],
        'counts':{'nodes':len(nodes),'connections':len(conns),'values':len(vals),'compounds':len(comps)},
        'node_types':dict(type_counts.most_common()),
        'edge_type_pairs':dict(edge_pairs.most_common()),
        'nodes':nodes,
        'connections':conns,
        'values':vals,
        'compounds':comps,
        'teaching_notes':notes,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source',type=pathlib.Path)
    ap.add_argument('out',type=pathlib.Path)
    args=ap.parse_args()
    src=args.source.resolve(); out=args.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    graphs=[]
    for p in sorted(src.rglob('*.json')):
        try:
            g=normalize_graph(p,src)
            if g: graphs.append(g)
        except Exception as e:
            print(f'WARN {p}: {e}')
    # write one compact record per graph for targeted access
    norm=out/'normalized'; norm.mkdir(exist_ok=True)
    for g in graphs:
        (norm/f"{g['id']}.json").write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    # indexes
    by_cat=collections.defaultdict(list); node_to_graphs=collections.defaultdict(list); pair_to_graphs=collections.defaultdict(list); versions=collections.defaultdict(list)
    for g in graphs:
        by_cat[g['category']].append(g['id'])
        for nt,count in g['node_types'].items(): node_to_graphs[nt].append({'graph':g['id'],'count':count,'category':g['category']})
        for ep,count in g['edge_type_pairs'].items(): pair_to_graphs[ep].append({'graph':g['id'],'count':count})
        for lib,ver in g['library_dependencies'].items(): versions[f'{lib}:{ver}'].append(g['id'])
    graph_index=[{k:g.get(k) for k in ('id','compound_name','category','description','documentation_file','library_dependencies','counts')} for g in graphs]
    (out/'graph-index.json').write_text(json.dumps(graph_index,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'node-usage-index.json').write_text(json.dumps(node_to_graphs,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    (out/'edge-pattern-index.json').write_text(json.dumps(pair_to_graphs,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    (out/'category-index.json').write_text(json.dumps(by_cat,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    (out/'version-index.json').write_text(json.dumps(versions,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    # Human workflow index
    lines=['# Autodesk Bifrost Workflow Corpus','',f'Normalized graphs: **{len(graphs)}**','',
           'Use `scripts/search_graph_examples.py` for targeted retrieval and `scripts/inspect_graph.py` for a graph summary.','', '## Categories','']
    for cat,names in sorted(by_cat.items(), key=lambda kv:(-len(kv[1]),kv[0].lower())):
        lines.append(f'### {cat} ({len(names)})')
        for gid in sorted(names):
            g=next(x for x in graphs if x['id']==gid)
            desc=(g.get('description') or '').strip().replace('\n',' ')
            lines.append(f'- **{gid}** — {desc}' if desc else f'- **{gid}**')
        lines.append('')
    (out/'workflow-index.md').write_text('\n'.join(lines),encoding='utf-8')
    # Corpus statistics / patterns
    common_nodes=collections.Counter(); common_edges=collections.Counter()
    for g in graphs:
        common_nodes.update(g['node_types']); common_edges.update(g['edge_type_pairs'])
    lines=['# Bifrost Workflow Patterns','',
           'These frequencies are derived from Autodesk-shipped example graphs. Treat them as retrieval hints, not universal rules.','',
           '## Most frequent node types','']
    for n,c in common_nodes.most_common(80): lines.append(f'- `{n}` — {c} occurrences')
    lines += ['', '## Most frequent node-to-node type connections','']
    for e,c in common_edges.most_common(100): lines.append(f'- `{e}` — {c} connections')
    (out/'workflow-patterns.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'Normalized {len(graphs)} graphs into {out}')

if __name__=='__main__': main()
