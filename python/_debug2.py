import csv
f = open('artifacts/sprint40_decision_observation.csv', 'r', encoding='utf-8')
rows = list(csv.DictReader(f))
f.close()
print('Sample observed notes:')
for r in rows:
    if 'Read first 20' in (r['observation_note'] or ''):
        print(r['repo'], r['issue'], repr(r['observation_note'][:80]))
print('---')
for r in rows:
    note = r['observation_note'] or ''
    if 'Human observation required' not in note:
        print(r['repo'], r['issue'], repr(note[:80]))
