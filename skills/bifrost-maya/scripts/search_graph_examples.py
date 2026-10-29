#!/usr/bin/env python3
"""Search the normalized Autodesk Bifrost example graphs.

Scores each graph by where the query words appear, not how often: a word in the
graph's name counts most, then its category and description, then the node
types it uses, and its long documentation counts least (capped), so large,
heavily documented graphs don't win on volume alone.
"""
import argparse
import json
import pathlib
import re
import sys

STOPWORDS = {"a", "an", "and", "the", "on", "of", "in", "to", "with", "for", "by", "from", "into", "onto",
             "at", "is", "it", "as", "or", "using", "use", "make", "create", "graph", "example", "some"}


def load(data):
    return json.loads((data / 'graph-index.json').read_text(encoding='utf-8'))


def stem(token):
    return token[:-1] if len(token) > 4 and token.endswith('s') else token


def score_graph(graph, normalized, tokens):
    name = graph['id'].lower().replace('_', ' ')
    summary = ' '.join(str(graph.get(k) or '') for k in ('category', 'description', 'compound_name')).lower()
    nodes = ' '.join(normalized.get('node_types', {})).lower() if normalized else ''
    docs = (normalized.get('documentation') or '').lower() if normalized else ''
    score = 0
    for token in tokens:
        if token in name:
            score += 10
        if token in summary:
            score += 4
        if token in nodes:
            score += 3
        score += min(docs.count(token), 3)
    return score


def main():
    ap = argparse.ArgumentParser(description='Search normalized Autodesk Bifrost example graphs.')
    ap.add_argument('query')
    ap.add_argument('--data', type=pathlib.Path,
                    default=pathlib.Path(__file__).resolve().parents[1] / 'references' / 'workflow-data')
    ap.add_argument('--limit', type=int, default=12)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    tokens = [stem(t) for t in re.split(r'\W+', args.query.lower()) if t and t not in STOPWORDS]
    rows = []
    for graph in load(args.data):
        path = args.data / 'normalized' / f"{graph['id']}.json"
        normalized = None
        if path.exists():
            try:
                normalized = json.loads(path.read_text(encoding='utf-8'))
            except ValueError:
                pass
        score = score_graph(graph, normalized, tokens)
        if score:
            rows.append((score, graph))
    for score, graph in sorted(rows, key=lambda x: (-x[0], x[1]['id']))[:args.limit]:
        print(f"{score:4d}  {graph['id']}  [{graph.get('category')}]\n      {graph.get('description') or ''}")


if __name__ == '__main__':
    main()
