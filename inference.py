#!/usr/bin/env python3
import os
import sys
import json
import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")

def run_episode(task_id):
    rewards = []
    steps_taken = 0
    success = False
    
    try:
        print(f"[START] task={task_id} env=debugtrace model={MODEL_NAME}")
        sys.stdout.flush()
        
        reset_resp = requests.post(f"{ENV_BASE_URL}/reset", json={"task_id": task_id}, timeout=10).json()
        broken = reset_resp['broken_code']
        desc = reset_resp['description']
        
        prompt = f"Fix this Python bug.\nTask: {desc}\nBroken:\n{broken}\nReturn ONLY the exact fixed function block. No ticks."
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=600
        )
        fixed = response.choices[0].message.content.strip()
        if fixed.startswith('```'):
            fixed = '\n'.join(fixed.split('\n')[1:-1])

        step_resp = requests.post(f"{ENV_BASE_URL}/step", json={"fixed_code": fixed}, timeout=10).json()
        reward = step_resp.get('score', 0.0)
        done = step_resp.get('done', True)
        
        err = step_resp.get('error', None)
        err_str = json.dumps(err) if err else "null"
        
        print(f"[STEP] step=1 action=submit_fix reward={reward:.2f} done={str(done).lower()} error={err_str}")
        sys.stdout.flush()
        rewards.append(reward)
        steps_taken = 1
        
        if reward >= 1.0:
            success = True
            
    except Exception as e:
        print(f"[STEP] step=1 action=submit_fix reward=0.00 done=true error={json.dumps(str(e))}")
        sys.stdout.flush()
        rewards.append(0.00)
        steps_taken = 1
        
    finally:
        rewards_str = ",".join(f"{r:.2f}" for r in rewards)
        print(f"[END] success={str(success).lower()} steps={steps_taken} rewards={rewards_str}")
        sys.stdout.flush()

def main():
    try:
        for task_id in ['easy', 'medium', 'hard']:
            run_episode(task_id)
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()
