#!/usr/bin/env python3
"""
Test script to verify varying scores with partial fixes
"""
import requests

BASE_URL = 'http://localhost:7860'

print("=" * 70)
print("Testing Varying Scores with Partial and Full Fixes")
print("=" * 70)

# Test 1: Completely wrong fix
print("\n--- TEST 1: Completely Wrong Fix (0 tests pass) ---")
requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': 'return None'})
score1 = resp.json()['score']
print(f"Score: {score1}")
assert 0 < score1 < 1, f"Score must be in (0, 1), got {score1}"

# Test 2: Partial fix (some tests pass)
print("\n--- TEST 2: Partial Fix (partial tests pass) ---")
requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
partial_fix = '''def sum_list(nums):
    total = 0
    for i in range(len(nums)):
        total += i  # Bug: using i instead of nums[i]
    return total'''
resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': partial_fix})
score2 = resp.json()['score']
print(f"Score: {score2}")
assert 0 < score2 < 1, f"Score must be in (0, 1), got {score2}"

# Test 3: Correct fix (all tests pass)
print("\n--- TEST 3: Correct Fix (all tests pass) ---")
requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
correct_fix = '''def sum_list(nums):
    total = 0
    for i in range(len(nums)):
        total += nums[i]
    return total'''
resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': correct_fix})
score3 = resp.json()['score']
print(f"Score: {score3}")
assert 0 < score3 < 1, f"Score must be in (0, 1), got {score3}"

# Verify scores are different
print("\n" + "=" * 70)
print("SCORE VARIATION TEST")
print("=" * 70)
print(f"Wrong fix:    {score1}")
print(f"Partial fix:  {score2}")
print(f"Correct fix:  {score3}")
print()

if score1 < score2 < score3:
    print("✓ Scores properly vary from wrong → partial → correct!")
else:
    print(f"✗ Scores should increase: {score1} < {score2} < {score3}")
    if not (score1 < score2 < score3):
        print("  Problem: Scores are not ordered correctly")

# Verify all are in range
print()
if all(0 < s < 1 for s in [score1, score2, score3]):
    print("✓ All scores are strictly in range (0, 1)")
else:
    print("✗ Some scores are NOT in range (0, 1)")
