#!/usr/bin/env python3
import argparse,json,pathlib,re

def load(data):
    return json.loads((data/'graph-index.json').read_text(encoding='utf-8'))

def main():
    ap=argparse.ArgumentParser(description='Search normalized Autodesk Bifrost example graphs.')
    ap.add_argument('query')
    ap.add_argument('--data',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]/'references'/'workflow-data')
    ap.add_argument('--limit',type=int,default=12)
    args=ap.parse_args(); q=args.query.lower(); toks=[t for t in re.split(r'\W+',q) if t]
    rows=[]
    for g in load(args.data):
        hay=' '.join(str(g.get(k) or '') for k in ('id','category','description','compound_name')).lower()
        score=sum(hay.count(t) for t in toks)
        p=args.data/'normalized'/f"{g['id']}.json"
        if p.exists():
            try:
                d=json.loads(p.read_text(encoding='utf-8'))
                nodehay=' '.join(d.get('node_types',{})).lower()
                score+=sum(nodehay.count(t)*2 for t in toks)
                dochay=(d.get('documentation') or '').lower()
                score+=sum(dochay.count(t) for t in toks)
            except Exception: pass
        if score: rows.append((score,g))
    for score,g in sorted(rows,key=lambda x:(-x[0],x[1]['id']))[:args.limit]:
        print(f"{score:4d}  {g['id']}  [{g.get('category')}]\n      {g.get('description') or ''}")

if __name__=='__main__': main()
