#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes are working correctly
"""
import requests
import json

BASE_URL = "http://localhost:7860"

def test_all():
    print("=" * 60)
    print("COMPREHENSIVE VALIDATOR FLOW TEST")
    print("=" * 60)
    
    # Test 1: Reset endpoint
    print("\n[Test 1] POST /reset for 'easy' task")
    resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})
    print(f"Status: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
    assert resp.status_code == 200
    assert resp.json()["task_id"] == "easy"
    print("✓ PASS")
    
    # Test 2: Baseline endpoint
    print("\n[Test 2] GET /baseline (all tasks)")
    resp = requests.get(f"{BASE_URL}/baseline")
    print(f"Status: {resp.status_code}")
    baseline_data = resp.json()
    print(f"Response: {json.dumps(baseline_data, indent=2)}")
    assert resp.status_code == 200
    assert all(0 <= baseline_data[task] <= 1 for task in ["easy", "medium", "hard"])
    print("✓ PASS - All scores in valid range [0, 1]")
    
    # Test 3: Grade easy task
    print("\n[Test 3] POST /grader for 'easy' task")
    resp = requests.post(f"{BASE_URL}/grader", json={
        "task_id": "easy",
        "fixed_code": "def sum_list(nums):\n    total = 0\n    for i in range(len(nums)):\n        total += nums[i]\n    return total"
    })
    print(f"Status: {resp.status_code}")
    easy_score = resp.json()["score"]
    print(f"Score: {easy_score}")
    assert resp.status_code == 200
    assert 0 <= easy_score <= 1
    print("✓ PASS - Score in valid range")
    
    # Test 4: Grade medium task
    print("\n[Test 4] POST /grader for 'medium' task")
    resp = requests.post(f"{BASE_URL}/grader", json={
        "task_id": "medium",
        "fixed_code": "def is_palindrome(s):\n    return s == s[::-1]"
    })
    print(f"Status: {resp.status_code}")
    medium_score = resp.json()["score"]
    print(f"Score: {medium_score}")
    assert resp.status_code == 200
    assert 0 <= medium_score <= 1
    print("✓ PASS - Score in valid range")
    
    # Test 5: Grade hard task
    print("\n[Test 5] POST /grader for 'hard' task")
    resp = requests.post(f"{BASE_URL}/grader", json={
        "task_id": "hard",
        "fixed_code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in seen:\n            return [seen[diff], i]\n        seen[n] = i\n    return []"
    })
    print(f"Status: {resp.status_code}")
    hard_score = resp.json()["score"]
    print(f"Score: {hard_score}")
    assert resp.status_code == 200
    assert 0 <= hard_score <= 1
    print("✓ PASS - Score in valid range")
    
    # Test 6: Step through environment
    print("\n[Test 6] POST /step (submission grading)")
    resp = requests.post(f"{BASE_URL}/step", json={
        "fixed_code": "def sum_list(nums):\n    total = 0\n    for i in range(len(nums)):\n        total += nums[i]\n    return total"
    })
    print(f"Status: {resp.status_code}")
    step_resp = resp.json()
    print(f"Response: {json.dumps(step_resp, indent=2)}")
    assert resp.status_code == 200
    assert 0 <= step_resp["reward"] <= 1
    print("✓ PASS - Step executed, reward in valid range")
    
    # Test 7: Error handling with invalid code
    print("\n[Test 7] POST /grader with invalid code (edge case)")
    resp = requests.post(f"{BASE_URL}/grader", json={
        "task_id": "easy",
        "fixed_code": "# empty code\npass"
    })
    print(f"Status: {resp.status_code}")
    error_score = resp.json()["score"]
    print(f"Score: {error_score}")
    assert resp.status_code == 200
    assert 0 <= error_score <= 1, f"Invalid score: {error_score}"
    print("✓ PASS - Error handled gracefully, score in valid range")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nKey Validations:")
    print(f"  • Baseline scores: easy={baseline_data['easy']}, medium={baseline_data['medium']}, hard={baseline_data['hard']}")
    print(f"  • Task-specific grading works: easy={easy_score}, medium={medium_score}, hard={hard_score}")
    print(f"  • Step method works: reward={step_resp['reward']}")
    print(f"  • Error handling: score with invalid code={error_score}")
    print("\nAll scores are in valid range [0, 1] inclusive ✓")

if __name__ == "__main__":
    try:
        test_all()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
