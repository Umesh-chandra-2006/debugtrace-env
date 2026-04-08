#!/usr/bin/env python3
"""
DebugTraceEnv Inference Script
Evaluates an LLM agent (via OpenAI Client) on code debugging tasks.

Uses OpenAI-compatible OpenRouter API endpoint.
Outputs [START], [STEP], [END] format for hackathon submission.
"""

import os
import sys
import json
import requests
from openai import OpenAI

# Environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client pointing to OpenRouter API
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Environment server URL (local or remote)
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

def fix_code_with_llm(broken_code, task_description):
    """
    Use OpenAI Client to generate a fix for broken code via OpenRouter API.
    """
    prompt = f"""You are an expert Python developer. Fix the following broken Python function.

Task: {task_description}

Broken Code:
{broken_code}

Return ONLY the fixed function code. Do not include explanations or test cases. 
Keep the function signature exactly the same."""
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )
        fixed_code = response.choices[0].message.content.strip()
        
        # Clean up markdown code blocks if present
        if fixed_code.startswith('```'):
            fixed_code = '\n'.join(fixed_code.split('\n')[1:-1])
        
        return fixed_code
    except Exception as e:
        print(f"# Error calling LLM: {e}", file=sys.stderr)
        return ""

def run_episode(task_id):
    """
    Run a single episode: reset environment, get task, fix with LLM, step.
    Output in [START]/[STEP]/[END] format.
    """
    rewards = []
    steps_taken = 0
    last_error = None
    success = False
    
    try:
        # [START]
        print(f"[START] task={task_id} env=debugtrace model={MODEL_NAME}")
        
        # Reset environment
        reset_resp = requests.post(
            f"{ENV_BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=10
        ).json()
        
        broken_code = reset_resp['broken_code']
        description = reset_resp['description']
        
        # Fix code with LLM
        fixed_code = fix_code_with_llm(broken_code, description)
        
        if not fixed_code:
            last_error = "LLM returned empty code"
            # [STEP] - failed attempt
            print(f"[STEP] step=1 action=submit_fix reward=0.00 done=true error={json.dumps(last_error)}")
            rewards.append(0.0)
            steps_taken = 1
        else:
            # Submit fix to environment
            step_resp = requests.post(
                f"{ENV_BASE_URL}/step",
                json={"fixed_code": fixed_code},
                timeout=10
            ).json()
            
            reward = step_resp.get('score', 0.0)
            done = step_resp.get('done', True)
            
            # [STEP]
            error_msg = step_resp.get('error', None)
            error_str = json.dumps(error_msg) if error_msg else "null"
            print(f"[STEP] step=1 action=submit_fix reward={reward:.2f} done={str(done).lower()} error={error_str}")
            
            rewards.append(reward)
            steps_taken = 1
            
            if reward == 1.0:
                success = True
    
    except Exception as e:
        last_error = str(e)
        print(f"[STEP] step=1 action=submit_fix reward=0.00 done=true error={json.dumps(last_error)}")
        rewards.append(0.0)
        steps_taken = 1
    
    # [END]
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps_taken} rewards={rewards_str}")

def main():
    """
    Main entry point: run all three tasks.
    """
    try:
        for task_id in ['easy', 'medium', 'hard']:
            run_episode(task_id)
            print()  # Blank line between episodes
    except KeyboardInterrupt:
        print("# Interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"# Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
