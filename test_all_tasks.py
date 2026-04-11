import requests
import json

space_url = 'https://umesh-tirumani-debugtrace-env.hf.space'

print('=== Testing All Three Task Levels on Live Space ===')
print()

for task_level in ['easy', 'medium', 'hard']:
    print(f'--- Testing {task_level.upper()} ---')
    
    # Reset
    reset_resp = requests.post(
        f'{space_url}/reset',
        json={'task_id': task_level},
        timeout=15
    ).json()
    
    print(f'Task Description: {reset_resp["description"][:60]}...')
    print(f'Broken Code: {reset_resp["broken_code"][:80]}...')
    
    # Submit a simple fix (just to test the endpoint)
    fixed = reset_resp['broken_code'].replace('+ 1', '')  # Remove obvious bug
    step_resp = requests.post(
        f'{space_url}/step',
        json={'fixed_code': fixed},
        timeout=15
    ).json()
    
    reward = step_resp.get('score', 0.0)
    passed = step_resp.get('passed', False)
    
    print(f'Result: reward={reward}, passed={passed}')
    print()
    
    # Show format
    error_str = json.dumps(step_resp.get('error')) if step_resp.get('error') else 'null'
    print(f'[START] task={task_level} env=debugtrace model=nvidia/nemotron-3-super-120b-a12b:free')
    print(f'[STEP] step=1 action=submit_fix reward={reward:.2f} done=true error={error_str}')
    print(f'[END] success={str(reward == 1.0).lower()} steps=1 rewards={reward:.2f}')
    print()
