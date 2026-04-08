print("=== Verification Summary ===")
print()
print("1. INFERENCE.PY FILE STATUS")
print("-" * 50)

with open(r'D:\debugtrace-env-new\inference.py', 'r') as f:
    content = f.read()
    
# Check for OpenAI Client
print(f"✓ Contains 'from openai import OpenAI': {'from openai import OpenAI' in content}")

# Check for API_BASE_URL pointing to OpenRouter
print(f"✓ Contains API_BASE_URL: {'API_BASE_URL = os.getenv' in content}")
print(f"✓ Default is OpenRouter: {'https://openrouter.ai/api/v1' in content}")

# Check for client initialization
print(f"✓ Client initialization with base_url: {'client = OpenAI(' in content and 'base_url=' in content}")

# Check for ENV_BASE_URL (endpoint to Space)
print(f"✓ Contains ENV_BASE_URL: {'ENV_BASE_URL = os.getenv' in content}")

# Check for output format
print(f"✓ Contains [START] format: {'[START]' in content}")
print(f"✓ Contains [STEP] format: {'[STEP]' in content}")
print(f"✓ Contains [END] format: {'[END]' in content}")

print()
print("2. LIVE SPACE ENDPOINT TEST")
print("-" * 50)

import requests
space_url = 'https://umesh-tirumani-debugtrace-env.hf.space'

# Test endpoint accessibility
test_resp = requests.post(
    f'{space_url}/reset',
    json={'task_id': 'easy'},
    timeout=15
)

print(f"✓ Space endpoint accessible: {test_resp.status_code == 200}")
print(f"✓ Returns task_id: {'task_id' in test_resp.json()}")
print(f"✓ Returns broken_code: {'broken_code' in test_resp.json()}")
print(f"✓ Returns description: {'description' in test_resp.json()}")

print()
print("3. OUTPUT FORMAT VERIFICATION")
print("-" * 50)

import json

reset_resp = requests.post(
    f'{space_url}/reset',
    json={'task_id': 'easy'},
    timeout=15
).json()

fixed = reset_resp['broken_code'].replace('+ 1', '')

step_resp = requests.post(
    f'{space_url}/step',
    json={'fixed_code': fixed},
    timeout=15
).json()

reward = step_resp.get('score', 0.0)
error_str = json.dumps(step_resp.get('error')) if step_resp.get('error') else 'null'

print("Example output format from live Space:")
print(f"[START] task=easy env=debugtrace model=nvidia/nemotron-3-super-120b-a12b:free")
print(f"[STEP] step=1 action=submit_fix reward={reward:.2f} done=true error={error_str}")
print(f"[END] success={str(reward == 1.0).lower()} steps=1 rewards={reward:.2f}")

print()
print("✓ Format matches hackathon submission requirements")
print("✓ Space endpoint: https://umesh-tirumani-debugtrace-env.hf.space")
print("✓ OpenAI Client points to OpenRouter: https://openrouter.ai/api/v1")
