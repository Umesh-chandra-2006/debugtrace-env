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

@app.post('/step', response_model=StepResponse)
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
def grader(req: StepRequest):
    if not env.current_task:
        env.reset('easy')  # auto-init to easy task
    score = env._grade(req.fixed_code)
    return {'score': score, 'passed': score >= 0.99}

@app.post('/baseline')
def baseline():
    import baseline as bl
    return bl.run_baseline()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=7860)
