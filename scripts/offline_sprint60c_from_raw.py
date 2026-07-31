#!/usr/bin/env python3
"""
SPRINT 60C offline fallback: build decision trajectory artifacts from data/langgraph_raw.json.
Avoids live GitHub API/rate limits.
"""
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

RAW = 'data/langgraph_raw.json'
OUT = 'data/trajectories/langchain_ai_langgraph'
os.makedirs(OUT, exist_ok=True)

raw = json.load(open(RAW, 'r', encoding='utf-8'))
issues = raw.get('issues', []) or []
pulls = raw.get('pulls', []) or []
commits = raw.get('commits', []) or []

def detect(text):
    t = text.lower()
    sigs = []
    for pat, typ in [
        (r'we decided to', 'explicit_decision'), ('decision:', 'explicit_decision'), ('chose to', 'explicit_decision'),
        ('chosen to', 'explicit_decision'), ('opted for', 'explicit_decision'), ('went with', 'explicit_decision'),
        ('picked', 'explicit_decision'), ('selected', 'explicit_decision'), ('switched to', 'switch'),
        ('replaced', 'switch'), ('replaced by', 'superseded'), ('superseded', 'superseded'), ('supersedes', 'superseded'),
        ('instead of', 'alternative_considered'), ('rather than', 'alternative_considered'), ('will be removed', 'removal'),
        ('will be deprecated', 'deprecation'), ('plan to remove', 'removal_plan'), ('no longer', 'removal'),
        ('abandoned', 'abandonment'), ('archived', 'archival'), ('not pursued', 'not_pursued'),
        ("won't implement", 'rejection'), ('will not', 'rejection'), ('successfully', 'success_indicator'),
        ('completed', 'completion'), ('finished', 'completion'), ('failed', 'failure_indicator'),
        ("didn't work", 'failure'), ('did not work', 'failure'), ('issues with', 'problems')
    ]:
        if pat in t:
            sigs.append(typ)
    return list(set(sigs))

def outcome_for(art):
    at = art['artifact_type']
    if at == 'pr':
        return 'success' if art.get('merged') else ('abandoned' if art.get('closed_at') else 'pending')
    if at == 'issue':
        state = art.get('state', '')
        labels = [l.lower() for l in art.get('labels', [])]
        if state == 'closed':
            if 'wontfix' in labels or 'obsolete' in labels:
                return 'abandoned'
            if 'duplicate' in labels:
                return 'superseded'
            return 'success'
        if state == 'open':
            sigs = art.get('signals', [])
            return 'abandoned' if any(s in sigs for s in ['abandonment','archival','not_pursued','rejection']) else 'pending'
        return 'pending'
    if at == 'commit':
        sigs = art.get('signals', [])
        if any(s in sigs for s in ['failure','rejection','removal']):
            return 'failure'
        return 'success'
    return 'unknown'

def confidence_for(art):
    conf = 0.5
    sigs = art.get('signals', [])
    if any('explicit' in s for s in sigs):
        conf += 0.3
    if any(s in sigs for s in ['switch','superseded','alternative_considered']):
        conf += 0.1
    body = art.get('body', art.get('message', ''))
    if body and len(body) > 100:
        conf += 0.1
    return max(0.1, min(conf, 1.0))

def timestamp_for(art):
    for f in ['closed_at','merged_at','updated_at','created_at']:
        if art.get(f):
            return art[f]
    return ''

def rationale_for(art):
    body = art.get('body', art.get('message', ''))
    for ind in ['because:', 'because ', 'since:', 'since ', 'due to:', 'due to ', 'reason:', 'rationale:', 'motivation:', 'motivation ']:
        idx = body.lower().find(ind)
        if idx != -1:
            snip = body[idx:idx+200]
            return snip.strip()
    return ''

arts = []
for it in issues:
    if 'pull_request' in it:
        continue
    sigs = detect((it.get('title','')+' '+it.get('body','')).lower())
    if not sigs:
        continue
    arts.append({
        'artifact_type':'issue','artifact_id':it['number'],'title':it.get('title',''),
        'body':(it.get('body') or '')[:500],'created_at':it.get('created_at',''),
        'updated_at':it.get('updated_at',''),'closed_at':it.get('closed_at'),
        'labels':[l.get('name','') for l in it.get('labels',[]) if isinstance(l,dict)],
        'signals':sigs,'url':it.get('html_url',''),
        'author': it.get('user',{}).get('login','') if isinstance(it.get('user'),dict) else ''
    })
for pr in pulls:
    title = pr.get('title') or ''
    body = pr.get('body') or ''
    sigs = detect((title+' '+body).lower())
    if not sigs:
        continue
    arts.append({
        'artifact_type':'pr','artifact_id':pr['number'],'title':title[:200],
        'body':body[:500],'created_at':pr.get('created_at',''),
        'updated_at':pr.get('updated_at',''),'closed_at':pr.get('closed_at'),
        'merged_at':pr.get('merged_at'),'merged':bool(pr.get('merged_at')),
        'signals':sigs,'url':pr.get('html_url',''),
        'author': pr.get('user',{}).get('login','') if isinstance(pr.get('user'),dict) else ''
    })
for c in commits:
    cd = c.get('commit',{}) if isinstance(c.get('commit'),dict) else {}
    msg = cd.get('message','') if isinstance(cd,dict) else ''
    author = cd.get('author',{}) if isinstance(cd,dict) else {}
    sigs = detect(msg)
    if sigs:
        arts.append({
            'artifact_type':'commit','artifact_id':c.get('sha','')[:7],
            'title':'','body':msg[:500],'message':msg[:500],'created_at':author.get('date','') if isinstance(author,dict) else '',
            'updated_at':'', 'closed_at':'', 'merged_at':'', 'merged':False,
            'signals':sigs,'url':c.get('html_url',''),
            'author': author.get('name','') if isinstance(author,dict) else ''
        })

decisions = []
for i,a in enumerate(arts,1):
    decisions.append({
        'decision_id': f'DECISION-{i:06d}', 'repository': 'langchain-ai/langgraph',
        'artifact_type': a['artifact_type'], 'artifact_id': a['artifact_id'], 'artifact_url': a['url'],
        'title': a.get('title','')[:200], 'body_snippet': a.get('body','')[:300],
        'actor': a.get('author',''), 'timestamp': timestamp_for(a), 'signals': a.get('signals',[]),
        'outcome': outcome_for(a), 'confidence': confidence_for(a), 'rationale': rationale_for(a),
        'labels': a.get('labels',[])
    })

out_dec = os.path.join(OUT, 'decisions_classified.jsonl')
with open(out_dec,'w',encoding='utf-8') as f:
    for d in decisions:
        f.write(json.dumps(d, ensure_ascii=False, default=str)+'\n')

nodes = decisions
ref_map = {}
for d in nodes:
    txt = d.get('title','')+' '+d.get('body_snippet','')+' '+d.get('rationale','')
    for m in re.finditer(r'#(\d+)', txt):
        ref='DECISION-'+m.group(1).zfill(6)
        ref_map.setdefault(ref, []).append(d['decision_id'])

edges = []
for sid, targets in ref_map.items():
    for tid in targets:
        edges.append({'from': sid,'to': tid,'type':'supported_by','evidence':'explicit_ref','confidence':0.85})

actor_groups = defaultdict(list)
for d in nodes:
    if d.get('actor'):
        actor_groups[d['actor']].append(d)
for actor in actor_groups:
    g = sorted(actor_groups[actor], key=lambda x:x.get('timestamp',''))
    for a,b in zip(g,g[1:]):
        edges.append({'from':a['decision_id'],'to':b['decision_id'],'type':'led_to','evidence':'same_actor_temporal','confidence':0.4})

outcomes = Counter(d.get('outcome','unknown') for d in nodes)
graph = {
  'graph_id':'EG-000001','request_id':'ER-000001','repository':'langchain-ai/langgraph',
  'trajectory_id':'DT-000001','root_decision': nodes[0]['decision_id'] if nodes else None,
  'nodes': nodes, 'edges': edges,
  'provenance': {'generated_by':'CoResearcher','timestamp': datetime.now().isoformat(),'repository':'langchain-ai/langgraph','reconstruction_method':'full'},
  'metrics': {
    'total_decisions': len(nodes),
    'successful_decisions': int(outcomes.get('success',0)),
    'abandoned_decisions': int(outcomes.get('abandoned',0)),
    'superseded_decisions': int(outcomes.get('superseded',0)),
    'failed_decisions': int(outcomes.get('failure',0)),
    'pending_decisions': int(outcomes.get('pending',0)),
    'unique_actors': len(actor_groups),
    'edges': len(edges),
    'explicit_ref_edges': sum(1 for e in edges if e.get('evidence')=='explicit_ref'),
    'temporal_edges': sum(1 for e in edges if e.get('evidence')=='same_actor_temporal')
  }
}
with open(os.path.join(OUT,'trajectory_graph.json'),'w',encoding='utf-8') as f:
    json.dump(graph, f, ensure_ascii=False, indent=2, default=str)
with open(os.path.join(OUT,'evaluation_metrics.json'),'w',encoding='utf-8') as f:
    json.dump(graph['metrics'], f, ensure_ascii=False, indent=2)
print(json.dumps(graph['metrics'], ensure_ascii=False, indent=2))