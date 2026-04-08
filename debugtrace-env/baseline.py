import requests
import os
import google.generativeai as genai

BASE_URL = 'http://localhost:7860'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def fix_code_with_gemini(broken_code, task_description):
    """
    Use Gemini API to generate a fix for broken code.
    """
    prompt = f"""You are an expert Python developer. Fix the following broken Python function.

Task: {task_description}

Broken Code:
{broken_code}

Return ONLY the fixed function code. Do not include explanations or test cases. 
Keep the function signature exactly the same."""
    
    try:
        response = model.generate_content(prompt, temperature=0.1, max_output_tokens=500)
        fixed_code = response.text.strip()
        # Clean up markdown code blocks if present
        if fixed_code.startswith('```'):
            fixed_code = '\n'.join(fixed_code.split('\n')[1:-1])
        return fixed_code
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
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
            
            # Get Gemini's fix
            print(f"Calling Gemini API to fix {task_id} task...")
            fixed_code = fix_code_with_gemini(broken_code, description)
            
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
