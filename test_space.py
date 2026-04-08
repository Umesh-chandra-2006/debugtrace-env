import requests
import json

space_url = 'https://umesh-tirumani-debugtrace-env.hf.space'

print('=== Testing Full Inference Workflow on Live Space ===')
print()

# Step 1: Reset environment
print('[1] Resetting environment...')
reset_resp = requests.post(
    f'{space_url}/reset',
    json={'task_id': 'easy'},
    timeout=15
).json()

print(f'Task ID: {reset_resp["task_id"]}')
print(f'Description: {reset_resp["description"]}')
print(f'Broken Code:')
print(reset_resp['broken_code'])
print()

# Step 2: Submit a fixed code
print('[2] Submitting fixed code...')
fixed_code = '''def sum_list(nums):
    total = 0
    for i in range(len(nums)):  # Fixed: removed +1
        total += nums[i]
    return total'''

step_resp = requests.post(
    f'{space_url}/step',
    json={'fixed_code': fixed_code},
    timeout=15
).json()

print('Step Response:')
print(json.dumps(step_resp, indent=2))
print()

# Step 3: Simulate what inference.py would output
print('[3] Simulating inference.py output format...')
print()

reward = step_resp.get('score', 0.0)
done = step_resp.get('done', True)
error_msg = step_resp.get('error', None)
error_str = json.dumps(error_msg) if error_msg else 'null'

print(f'[START] task=easy env=debugtrace model=nvidia/nemotron-3-super-120b-a12b:free')
print(f'[STEP] step=1 action=submit_fix reward={reward:.2f} done={str(done).lower()} error={error_str}')
print(f'[END] success={str(reward == 1.0).lower()} steps=1 rewards={reward:.2f}')
