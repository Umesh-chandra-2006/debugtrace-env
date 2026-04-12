#!/usr/bin/env python3
"""Test the validator flow"""
import requests
import json

print("=== Test 1: GET /baseline endpoint ===")
resp = requests.get('http://localhost:7860/baseline')
baseline = resp.json()
print(f"Status: {resp.status_code}")
print(f"Response: {json.dumps(baseline, indent=2)}")
print(f"All scores in range: {all(0 < v < 1 for v in baseline.values())}")

print("\n=== Test 2: POST /grader with task_id parameter ===")
# Test grader for each task
for task_id in ['easy', 'medium', 'hard']:
    correct_fixes = {
        'easy': 'def sum_list(nums):\n    total = 0\n    for i in range(len(nums)):\n        total += nums[i]\n    return total',
        'medium': 'def is_palindrome(s):\n    return s == s[::-1]',
        'hard': 'def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []'
    }
    resp = requests.post('http://localhost:7860/grader', json={
        'fixed_code': correct_fixes[task_id],
        'task_id': task_id
    })
    data = resp.json()
    score = data.get('score')
    print(f"{task_id}: score={score}, valid={0 < score < 1}")

print("\n=== Test 3: Validator flow simulation ===")
# Validator calls GET /baseline first
baseline_scores = requests.get('http://localhost:7860/baseline').json()
print(f"Baseline scores: {baseline_scores}")

# Then grader per task
for task_id in baseline_scores.keys():
    resp = requests.post('http://localhost:7860/grader', json={
        'fixed_code': '',  # empty code
        'task_id': task_id
    })
    data = resp.json()
    score = data.get('score')
    print(f"Grader {task_id} (empty code): score={score}, valid={0 < score < 1}")
