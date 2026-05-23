from backend.adrs_old.normalizer import normalize_delta_e

result = normalize_delta_e({'EGFR_signaling': 0.82, 'PI3K_AKT': 0.61, 'MAPK': 0.45, 'Apoptosis': 0.20})
print('Test 1 - normal:', result)
assert result['EGFR_signaling'] == 1.0, 'highest should be 1.0'
assert result['Apoptosis'] == 0.0, 'lowest should be 0.0'

result2 = normalize_delta_e({'A': 0.5, 'B': 0.5})
print('Test 2 - identical:', result2)
assert all(v == 1.0 for v in result2.values()), 'all should be 1.0'

result3 = normalize_delta_e({})
print('Test 3 - empty:', result3)
assert result3 == {}

print('All 3 tests passed')