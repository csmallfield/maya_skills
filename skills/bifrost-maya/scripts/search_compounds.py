#!/usr/bin/env python3
import argparse, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE.parent / 'references' / 'compound-data'


def tokens(s):
    return [x for x in re.findall(r'[a-z0-9_]+', (s or '').lower()) if len(x) > 1]


def score_record(rec, query_tokens):
    fields = {
        'id': 7,
        'root_names': 9,
        'collection': 5,
        'category': 5,
        'documentation_summary': 5,
        'documentation_search': 2,
        'port_names': 5,
        'node_types_search': 4,
        'dependencies_search': 4,
        'source_path': 2,
    }
    score = 0
    hits = []
    for field, weight in fields.items():
        val = rec.get(field, '')
        if isinstance(val, list): val = ' '.join(str(x) for x in val)
        text = str(val).lower()
        for tok in query_tokens:
            if tok in text:
                score += weight
                hits.append(f'{field}:{tok}')
    return score, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('query')
    ap.add_argument('--limit', type=int, default=12)
    ap.add_argument('--collection')
    args = ap.parse_args()
    idx = json.loads((DATA / 'compound-index.json').read_text(encoding='utf-8'))
    q = tokens(args.query)
    rows = []
    for rec in idx:
        if args.collection and rec.get('collection','').lower() != args.collection.lower():
            continue
        s, hits = score_record(rec, q)
        if s:
            rows.append((s, rec, hits))
    rows.sort(key=lambda x: (-x[0], x[1]['id']))
    for s, rec, hits in rows[:args.limit]:
        roots = ', '.join(x for x in rec.get('root_names', []) if x)
        print(f"{s:3d}  {rec['id']}  [{rec['collection']} / {rec['category']}]  {roots}")
        if rec.get('documentation_summary'):
            print('     ' + rec['documentation_summary'][:260])

if __name__ == '__main__': main()
