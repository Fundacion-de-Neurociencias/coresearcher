import csv, json

d = json.load(open('data/sprint40_candidates.json'))
csv_needed = [i['number'] for i in d['nilearn/nilearn']]

f = open('artifacts/sprint40_decision_observation.csv', 'r', encoding='utf-8')
rows = list(csv.DictReader(f))
f.close()

existing = {int(r['issue']) for r in rows if r['repo'] == 'nilearn/nilearn'}
missing = [i for i in csv_needed if i not in existing]
print('Missing:', missing)

note = 'Human observation required — full discussion not read.'
with open('artifacts/sprint40_decision_observation.csv', 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    for issue in missing:
        w.writerow(['nilearn/nilearn', str(issue), '', '', '', '', '', '', note])

print('Added', len(missing), 'rows')
