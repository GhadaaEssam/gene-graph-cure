
import json
with open('backend/adrs/data/gdsc_index.json') as f:
    idx = json.load(f)

for i, (k, v) in enumerate(idx.items()):
    print(k, '|', v['drug_name'], '|', v['targets'])
    if i == 4: break

print()
e = idx.get('ERLOTINIB')
print('ERLOTINIB:', e)

