from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from env import DebugTraceEnv
from tasks import TASKS
import uvicorn

app = FastAPI(title='DebugTraceEnv')
env = DebugTraceEnv()

class ResetRequest(BaseModel):
    task_id: str = 'easy'

class StepRequest(BaseModel):
    fixed_code: str

class GraderRequest(BaseModel):
    fixed_code: str
    task_id: str = 'easy'

class Observation(BaseModel):
    task_id: str
    description: str
    broken_code: str
    stack_trace: str
    instruction: str

class ResetResponse(BaseModel):
    task_id: str
    description: str
    broken_code: str
    stack_trace: str
    instruction: str

class StepResponse(BaseModel):
    reward: float
    done: bool
    score: float
    passed: bool

@app.post('/reset', response_model=ResetResponse)
def reset(req: Optional[ResetRequest] = None):
    task_id = req.task_id if req else 'easy'
    return env.reset(task_id)

@app.post('/step')
def step(req: StepRequest):
    return env.step({'fixed_code': req.fixed_code})

@app.get('/state')
def state():
    return env.state()

@app.get('/schema')
def get_schema():
    return {
        "action_schema": StepRequest.model_json_schema(),
        "observation_schema": Observation.model_json_schema()
    }

@app.get('/tasks')
def list_tasks():
    return [{'id': t['id'], 'description': t['description'], 
             'action_schema': {'fixed_code': 'string'}} for t in TASKS]

@app.get('/')
def health():
    return {'status': 'ok', 'service': 'DebugTraceEnv'}

@app.get('/logs')
def get_logs():
    return {'logs': []}

@app.post('/grader')
def grader(req: GraderRequest):
    env.reset(req.task_id)  # reset to requested task
    score = env._grade(req.fixed_code)
    return {'score': score, 'passed': score >= 0.99}

@app.get('/baseline')
def baseline():
    """Run baseline for all tasks and return scores"""
    results = {}
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
    for task_id, fix in correct_fixes.items():
        env.reset(task_id)
        score = env._grade(fix)
        results[task_id] = score
    return results

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7860)
