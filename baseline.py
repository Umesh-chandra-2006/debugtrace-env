import requests
import os

BASE_URL = 'http://localhost:7860'
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

def fix_code_with_nemotron(broken_code, task_description):
    """
    Use OpenRouter's Nemotron model to generate a fix for broken code.
    """
    prompt = f"""You are an expert Python developer. Fix the following broken Python function.

Task: {task_description}

Broken Code:
{broken_code}

Return ONLY the fixed function code. Do not include explanations or test cases. 
Keep the function signature exactly the same."""
    
    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://huggingface.co/spaces/umesh-tirumani/debugtrace-env",
                "X-Title": "DebugTraceEnv"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
        )
        
        if response.status_code != 200:
            print(f"OpenRouter API error: {response.status_code} - {response.text}")
            return ""
        
        result = response.json()
        fixed_code = result['choices'][0]['message']['content'].strip()
        
        # Clean up markdown code blocks if present
        if fixed_code.startswith('```'):
            fixed_code = '\n'.join(fixed_code.split('\n')[1:-1])
        return fixed_code
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return ""

def run_baseline():
    results = {}
    for task_id in ['easy', 'medium', 'hard']:
        try:
            # Reset environment and get task
            reset_resp = requests.post(f'{BASE_URL}/reset',
                                       json={'task_id': task_id}).json()
            broken_code = reset_resp['broken_code']
            description = reset_resp['description']
            
            print(f"\n{'='*60}")
            print(f"Task: {task_id.upper()}")
            print(f"Description: {description}")
            print(f"{'='*60}")
            
            # Get Nemotron's fix
            print(f"Calling OpenRouter Nemotron API to fix {task_id} task...")
            fixed_code = fix_code_with_nemotron(broken_code, description)
            
            if not fixed_code:
                results[task_id] = 0.0
                print(f"{task_id}: 0.0 (API call failed)")
                continue
            
            print(f"Fixed code:\n{fixed_code[:200]}...\n")
            
            # Submit fix and get score
            step_resp = requests.post(f'{BASE_URL}/step',
                                      json={'fixed_code': fixed_code}).json()
            score = step_resp.get('score', 0.0)
            results[task_id] = score
            print(f"{task_id}: {score} {'✓ PASSED' if score == 1.0 else '✗ FAILED'}")
            
        except Exception as e:
            print(f"Error processing {task_id}: {e}")
            results[task_id] = 0.0
    
    avg = sum(results.values()) / len(results) if results else 0.0
    print(f"\n{'='*60}")
    print(f"Average baseline score: {avg:.2f}")
    print(f"{'='*60}")
    return results

if __name__ == '__main__':
    run_baseline()
