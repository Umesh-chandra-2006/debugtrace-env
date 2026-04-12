import requests

BASE_URL = 'http://localhost:7860'

CORRECT_FIXES = {
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

def run_baseline():
    results = {}
    for task_id, fix in CORRECT_FIXES.items():
        try:
            requests.post(f'{BASE_URL}/reset', json={'task_id': task_id})
            step_resp = requests.post(f'{BASE_URL}/step', json={'fixed_code': fix}).json()
            
            # Get score and clamp to safe range (0.01, 0.99)
            score = step_resp.get('reward', 0.01)
            score = max(0.01, min(0.99, float(score)))
            results[task_id] = score
            print(f'{task_id}: {score}')
        except Exception as e:
            print(f'{task_id}: ERROR - {e}')
            results[task_id] = 0.01
        
    avg = sum(results.values()) / len(results) if results else 0.0
    print(f'Average baseline score: {avg}')
    return results

if __name__ == '__main__':
    run_baseline()
