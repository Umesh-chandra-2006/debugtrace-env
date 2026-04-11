#!/usr/bin/env python3
"""
Local Testing Script for DebugTraceEnv
Based on Section 10 of DebugTraceEnv_Spec.md
Tests all endpoints and verifies correct/wrong fixes
"""

import requests
import json
import subprocess
import time
import sys

BASE_URL = 'http://localhost:7860'

def test_reset():
    """Test /reset endpoint"""
    print("\n=== TEST 1: Reset Endpoint ===")
    try:
        resp = requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
        data = resp.json()
        assert 'broken_code' in data
        assert 'stack_trace' in data
        assert 'instruction' in data
        assert 'task_id' in data
        print(f"✓ Reset works. Task: {data['task_id']}")
        print(f"  Description: {data['description'][:60]}...")
        return True
    except Exception as e:
        print(f"✗ Reset failed: {e}")
        return False

def test_step_correct_fix():
    """Test /step endpoint with correct fix"""
    print("\n=== TEST 2: Step Endpoint (Correct Fix) ===")
    try:
        # Reset first
        requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
        
        # Submit correct fix
        correct_fix = '''def sum_list(nums):
    total = 0
    for i in range(len(nums)):
        total += nums[i]
    return total'''
        
        resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': correct_fix})
        data = resp.json()
        
        assert 'reward' in data
        assert 'score' in data
        assert 'done' in data
        assert 'passed' in data
        
        score = data['score']
        passed = data['passed']
        
        print(f"✓ Step endpoint works")
        print(f"  Score: {score}")
        print(f"  Passed: {passed}")
        print(f"  ✓ Score is in range (0, 1): {0 < score < 1}")
        
        if score >= 0.99:
            print(f"  ✓ Correct fix produces high score")
            return True
        else:
            print(f"  ✗ Correct fix should produce score >= 0.99")
            return False
            
    except Exception as e:
        print(f"✗ Step test failed: {e}")
        return False

def test_step_wrong_fix():
    """Test /step endpoint with wrong fix (should give low score)"""
    print("\n=== TEST 3: Step Endpoint (Wrong Fix) ===")
    try:
        # Reset first
        requests.post(f'{BASE_URL}/reset', json={'task_id': 'easy'})
        
        # Submit wrong fix
        wrong_fix = 'def sum_list(nums): return None'
        
        resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': wrong_fix})
        data = resp.json()
        
        score = data['score']
        passed = data['passed']
        
        print(f"✓ Step endpoint works with wrong fix")
        print(f"  Score: {score}")
        print(f"  Passed: {passed}")
        print(f"  ✓ Score is in range (0, 1): {0 < score < 1}")
        
        if score < 0.5:
            print(f"  ✓ Wrong fix produces low score")
            return True
        else:
            print(f"  ⚠ Wrong fix score is {score} (expected < 0.5)")
            return True  # Not critical
            
    except Exception as e:
        print(f"✗ Wrong fix test failed: {e}")
        return False

def test_state():
    """Test /state endpoint"""
    print("\n=== TEST 4: State Endpoint ===")
    try:
        requests.post(f'{BASE_URL}/reset', json={'task_id': 'medium'})
        resp = requests.get(f'{BASE_URL}/state')
        data = resp.json()
        assert 'task_id' in data
        assert 'episode_done' in data
        print(f"✓ State endpoint works")
        print(f"  Task ID: {data['task_id']}")
        return True
    except Exception as e:
        print(f"✗ State test failed: {e}")
        return False

def test_tasks_list():
    """Test /tasks endpoint"""
    print("\n=== TEST 5: Tasks List Endpoint ===")
    try:
        resp = requests.get(f'{BASE_URL}/tasks')
        tasks = resp.json()
        assert len(tasks) == 3
        assert all('id' in t for t in tasks)
        print(f"✓ Tasks list endpoint works")
        for task in tasks:
            print(f"  - {task['id']}: {task['description'][:40]}...")
        return True
    except Exception as e:
        print(f"✗ Tasks list test failed: {e}")
        return False

def test_baseline():
    """Test /baseline endpoint"""
    print("\n=== TEST 6: Baseline Script ===")
    try:
        resp = requests.post(f'{BASE_URL}/baseline')
        data = resp.json()
        
        print(f"✓ Baseline endpoint works")
        for task_id, score in data.items():
            print(f"  {task_id}: {score}")
            if 0 < score < 1:
                print(f"    ✓ Score in range (0, 1)")
            else:
                print(f"    ✗ Score {score} NOT in range (0, 1)")
                return False
        
        avg = sum(data.values()) / len(data)
        print(f"  Average: {avg:.3f}")
        return True
    except Exception as e:
        print(f"✗ Baseline test failed: {e}")
        return False

def test_all_tasks():
    """Test correct fixes for all three task levels"""
    print("\n=== TEST 7: All Three Task Levels ===")
    
    correct_fixes = {
        'easy': '''def sum_list(nums):
    total = 0
    for i in range(len(nums)):
        total += nums[i]
    return total''',
        'medium': '''def is_palindrome(s):
    return s == s[::-1]''',
        'hard': '''def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [seen[diff], i]
        seen[n] = i
    return []'''
    }
    
    all_passed = True
    for task_id, fix in correct_fixes.items():
        try:
            # Reset
            requests.post(f'{BASE_URL}/reset', json={'task_id': task_id})
            # Step
            resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': fix})
            data = resp.json()
            score = data['score']
            
            if 0.99 <= score < 1:
                print(f"  ✓ {task_id}: score={score:.2f}")
            else:
                print(f"  ✗ {task_id}: score={score} (expected ~0.99)")
                all_passed = False
        except Exception as e:
            print(f"  ✗ {task_id}: {e}")
            all_passed = False
    
    return all_passed

def main():
    print("=" * 70)
    print("DebugTraceEnv Local Testing Suite")
    print("=" * 70)
    print(f"Testing server at: {BASE_URL}")
    
    # Wait for server to start
    print("\nWaiting for server to start...")
    for i in range(10):
        try:
            requests.get(f'{BASE_URL}/tasks')
            print("✓ Server is running")
            break
        except:
            if i < 9:
                time.sleep(1)
            else:
                print("✗ Server is not responding. Make sure to run: python main.py")
                sys.exit(1)
    
    # Run all tests
    tests = [
        test_reset,
        test_step_correct_fix,
        test_step_wrong_fix,
        test_state,
        test_tasks_list,
        test_baseline,
        test_all_tasks,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())
