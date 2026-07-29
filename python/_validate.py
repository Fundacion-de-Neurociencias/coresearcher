import csv
f = open('artifacts/sprint40_decision_observation.csv', 'r', encoding='utf-8')
rows = list(csv.DictReader(f))
f.close()
print('Total rows:', len(rows))
obs = [r for r in rows if 'Human observation required' not in r['observation_note']]
print('Observed:', len(obs))
print('Decision YES:', sum(1 for r in obs if r['decision_exists'] == 'YES'))
print('Decision NO:', sum(1 for r in obs if r['decision_exists'] == 'NO'))
print('Alternatives YES:', sum(1 for r in obs if r['alternatives'] == 'YES'))
print('Disagreement YES:', sum(1 for r in obs if r['disagreement'] == 'YES'))
print('Recoverable YES:', sum(1 for r in obs if r['recoverable'] == 'YES'))
