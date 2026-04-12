**DebugTraceEnv**

Complete Build Specification

Scaler × Meta/PyTorch OpenEnv Hackathon --- Round 1

*Agent-to-build document · April 2026*

**1. What You Are Building**

DebugTraceEnv is a reinforcement learning environment where an AI agent
is given a broken Python function, a failing test, and a stack trace.
The agent must identify the root cause and produce a corrected version
of the function. The grader runs the fix against the test suite and
returns a score from 0.0 to 1.0.

This environment runs as a FastAPI web server inside a Docker container,
deployed publicly to Hugging Face Spaces. Judges will hit your public
URL, call the API endpoints, and verify correctness automatically.

**2. Project Architecture**

**2.1 File Structure**

Create the following file structure exactly:

> debugtrace-env/
>
> ├── main.py \# FastAPI app --- all endpoints
>
> ├── env.py \# Core environment logic
>
> ├── tasks.py \# All 3 task definitions
>
> ├── grader.py \# Grader logic (runs pytest)
>
> ├── openenv.yaml \# OpenEnv spec manifest
>
> ├── baseline.py \# Baseline agent script
>
> ├── Dockerfile \# Docker build file
>
> ├── requirements.txt \# Python dependencies
>
> └── README.md \# Setup + submission docs

**3. OpenEnv Specification**

**3.1 openenv.yaml**

This file is mandatory. Place it in the root of your project. It tells
the automated checker what your environment does.

> name: DebugTraceEnv
>
> version: 1.0.0
>
> description: \>
>
> An RL environment where an agent receives a broken Python
>
> function and must produce a corrected fix. Grader executes
>
> the fix against a test suite and returns a score 0.0--1.0.
>
> tasks:
>
> \- id: easy
>
> description: Fix a syntax or obvious runtime error
>
> difficulty: easy
>
> \- id: medium
>
> description: Fix a logic bug producing wrong output
>
> difficulty: medium
>
> \- id: hard
>
> description: Fix a multi-step algorithmic error
>
> difficulty: hard
>
> api:
>
> reset: POST /reset
>
> step: POST /step
>
> state: GET /state
>
> tasks: GET /tasks
>
> grader: POST /grader
>
> baseline: POST /baseline

**4. Tasks**

You need exactly 3 tasks. Define them in tasks.py as a list of dicts.
Each task has: id, description, broken_code, test_code, and
correct_output.

**Task 1 --- Easy (Syntax / Runtime Error)**

The broken function has a syntax error or a simple runtime error like
wrong variable name or off-by-one in a range.

> \# broken_code
>
> def sum_list(nums):
>
> total = 0
>
> for i in range(len(nums) + 1): \# bug: +1 causes IndexError
>
> total += nums\[i\]
>
> return total
>
> \# test_code
>
> def test_sum_list():
>
> assert sum_list(\[1, 2, 3\]) == 6
>
> assert sum_list(\[\]) == 0
>
> \# correct fix: change range(len(nums) + 1) to range(len(nums))

**Task 2 --- Medium (Logic Bug)**

The broken function runs without errors but produces wrong output due to
a logic mistake.

> \# broken_code
>
> def is_palindrome(s):
>
> return s == s\[1:\] \# bug: should be s\[::-1\]
>
> \# test_code
>
> def test_is_palindrome():
>
> assert is_palindrome(\'racecar\') == True
>
> assert is_palindrome(\'hello\') == False
>
> \# correct fix: change s\[1:\] to s\[::-1\]

**Task 3 --- Hard (Algorithmic Error)**

The broken function has a deeper bug --- wrong algorithm, missing edge
case, or incorrect data structure usage.

> \# broken_code
>
> def two_sum(nums, target):
>
> seen = {}
>
> for i, n in enumerate(nums):
>
> diff = target - n
>
> if diff in seen:
>
> return \[i, seen\[diff\]\] \# bug: indices reversed
>
> seen\[n\] = i
>
> return \[\]
>
> \# test_code
>
> def test_two_sum():
>
> assert two_sum(\[2, 7, 11, 15\], 9) == \[0, 1\]
>
> assert two_sum(\[3, 2, 4\], 6) == \[1, 2\]
>
> \# correct fix: return \[seen\[diff\], i\]

**5. Core Environment Logic (env.py)**

This is the brain of your environment. Paste this exactly into env.py.

> import subprocess, tempfile, os, json
>
> from tasks import TASKS
>
> class DebugTraceEnv:
>
> def \_\_init\_\_(self):
>
> self.current_task = None
>
> self.episode_done = False
>
> self.last_score = None
>
> def reset(self, task_id=\'easy\'):
>
> task = next((t for t in TASKS if t\[\'id\'\] == task_id), TASKS\[0\])
>
> self.current_task = task
>
> self.episode_done = False
>
> self.last_score = None
>
> return {
>
> \'task_id\': task\[\'id\'\],
>
> \'description\': task\[\'description\'\],
>
> \'broken_code\': task\[\'broken_code\'\],
>
> \'stack_trace\': task\[\'stack_trace\'\],
>
> \'instruction\': \'Return a fixed version of the function in
> fixed_code field\'
>
> }
>
> def step(self, action: dict):
>
> if self.episode_done:
>
> return {\'error\': \'Episode done. Call /reset first.\'}
>
> fixed_code = action.get(\'fixed_code\', \'\')
>
> score = self.\_grade(fixed_code)
>
> self.last_score = score
>
> self.episode_done = True
>
> return {
>
> \'reward\': score,
>
> \'done\': True,
>
> \'score\': score,
>
> \'passed\': score == 1.0
>
> }
>
> def state(self):
>
> return {
>
> \'task_id\': self.current_task\[\'id\'\] if self.current_task else
> None,
>
> \'episode_done\': self.episode_done,
>
> \'last_score\': self.last_score
>
> }
>
> def \_grade(self, fixed_code):
>
> task = self.current_task
>
> with tempfile.TemporaryDirectory() as tmpdir:
>
> code_file = os.path.join(tmpdir, \'solution.py\')
>
> test_file = os.path.join(tmpdir, \'test_solution.py\')
>
> with open(code_file, \'w\') as f:
>
> f.write(fixed_code)
>
> with open(test_file, \'w\') as f:
>
> f.write(\'from solution import \*\\n\')
>
> f.write(task\[\'test_code\'\])
>
> result = subprocess.run(
>
> \[\'python\', \'-m\', \'pytest\', test_file, \'-q\', \'\--tb=no\'\],
>
> capture_output=True, text=True, cwd=tmpdir, timeout=10
>
> )
>
> if \'1 passed\' in result.stdout:
>
> return 1.0
>
> elif \'2 passed\' in result.stdout:
>
> return 1.0
>
> elif \'passed\' in result.stdout:
>
> \# partial: count passed/total
>
> import re
>
> m = re.search(r\'(\\d+) passed\', result.stdout)
>
> if m: return min(float(m.group(1)) / 2.0, 1.0)
>
> elif result.returncode == 0:
>
> return 0.5 \# compiled, no crash, but no tests
>
> return 0.0

**6. FastAPI Server (main.py)**

This exposes all required endpoints. The automated checker will call
these URLs directly.

> from fastapi import FastAPI
>
> from pydantic import BaseModel
>
> from env import DebugTraceEnv
>
> from tasks import TASKS
>
> import uvicorn
>
> app = FastAPI(title=\'DebugTraceEnv\')
>
> env = DebugTraceEnv()
>
> class ResetRequest(BaseModel):
>
> task_id: str = \'easy\'
>
> class StepRequest(BaseModel):
>
> fixed_code: str
>
> \@app.post(\'/reset\')
>
> def reset(req: ResetRequest):
>
> return env.reset(req.task_id)
>
> \@app.post(\'/step\')
>
> def step(req: StepRequest):
>
> return env.step({\'fixed_code\': req.fixed_code})
>
> \@app.get(\'/state\')
>
> def state():
>
> return env.state()
>
> \@app.get(\'/tasks\')
>
> def list_tasks():
>
> return \[{\'id\': t\[\'id\'\], \'description\': t\[\'description\'\],
>
> \'action_schema\': {\'fixed_code\': \'string\'}} for t in TASKS\]
>
> \@app.post(\'/grader\')
>
> def grader(req: StepRequest):
>
> if not env.current_task:
>
> return {\'error\': \'No active task. Call /reset first.\'}
>
> score = env.\_grade(req.fixed_code)
>
> return {\'score\': score, \'passed\': score == 1.0}
>
> \@app.post(\'/baseline\')
>
> def baseline():
>
> import baseline as bl
>
> return bl.run_baseline()
>
> if \_\_name\_\_ == \'\_\_main\_\_\':
>
> uvicorn.run(app, host=\'0.0.0.0\', port=7860)

**7. Baseline Agent (baseline.py)**

This is not a real ML agent. It uses hardcoded correct answers to prove
the environment works. Judges run this to verify your grader produces
valid scores.

> import requests
>
> BASE_URL = \'http://localhost:7860\'
>
> CORRECT_FIXES = {
>
> \'easy\': \'\'\'def sum_list(nums):
>
> total = 0
>
> for i in range(len(nums)):
>
> total += nums\[i\]
>
> return total\'\'\',
>
> \'medium\': \'\'\'def is_palindrome(s):
>
> return s == s\[::-1\]\'\'\',
>
> \'hard\': \'\'\'def two_sum(nums, target):
>
> seen = {}
>
> for i, n in enumerate(nums):
>
> diff = target - n
>
> if diff in seen:
>
> return \[seen\[diff\], i\]
>
> seen\[n\] = i
>
> return \[\]\'\'\'
>
> }
>
> def run_baseline():
>
> results = {}
>
> for task_id, fix in CORRECT_FIXES.items():
>
> reset_resp = requests.post(f\'{BASE_URL}/reset\',
>
> json={\'task_id\': task_id}).json()
>
> step_resp = requests.post(f\'{BASE_URL}/step\',
>
> json={\'fixed_code\': fix}).json()
>
> results\[task_id\] = step_resp.get(\'score\', 0.0)
>
> print(f\'{task_id}: {results\[task_id\]}\')
>
> avg = sum(results.values()) / len(results)
>
> print(f\'Average baseline score: {avg}\')
>
> return results
>
> if \_\_name\_\_ == \'\_\_main\_\_\':
>
> run_baseline()

**8. Dockerfile**

This packages your entire environment so it runs identically anywhere
--- locally and on HuggingFace Spaces.

> FROM python:3.11-slim
>
> WORKDIR /app
>
> COPY requirements.txt .
>
> RUN pip install \--no-cache-dir -r requirements.txt
>
> COPY . .
>
> EXPOSE 7860
>
> CMD \[\"uvicorn\", \"main:app\", \"\--host\", \"0.0.0.0\",
> \"\--port\", \"7860\"\]

**requirements.txt**

> fastapi==0.110.0
>
> uvicorn==0.29.0
>
> pydantic==2.6.4
>
> pytest==8.1.1
>
> requests==2.31.0

**9. Deploying to HuggingFace Spaces**

Follow these steps in order after your code works locally.

1.  Create a free account at huggingface.co if you don\'t have one

2.  Click New Space → choose Docker as the SDK → name it debugtrace-env

3.  Install HuggingFace CLI: pip install huggingface_hub

4.  Run: huggingface-cli login (paste your HF token)

5.  Push your project: git init → git add . → git commit → git push to
    your HF space repo

6.  Your public URL will be:
    https://huggingface.co/spaces/YOUR_USERNAME/debugtrace-env

The Space will build automatically. Watch the logs on the HF dashboard
--- if the Dockerfile builds cleanly and the server starts, you are
live.

**10. How to Test (Read This Yourself)**

This section is for you --- not for the agent. Before submitting, run
every check below. If any of these fail, you will be disqualified
automatically.

**Step 1 --- Run Locally First**

Before Docker, test the raw server:

> pip install -r requirements.txt
>
> python main.py
>
> \# Server starts at http://localhost:7860

**Step 2 --- Test Each Endpoint Manually**

>
> \# Re-run all curl tests above against localhost:7860
>
> \# If they all pass → Docker is clean

If docker build fails, check your requirements.txt versions. If server
crashes on start, check for import errors in main.py.

**Step 6 --- Pre-Submission Checklist**

Run through this before pasting your HF URL:

  -----------------------------------------------------------------------
  **Check**                                     **Expected Result**
  --------------------------------------------- -------------------------
  POST /reset returns broken_code field         ✓ JSON with task data

  POST /step returns reward between 0.0--1.0    ✓ Float value

  GET /state returns episode status             ✓ JSON with task_id

  GET /tasks returns exactly 3 tasks            ✓ Array of 3 items

  POST /baseline returns scores for all 3 tasks ✓ {easy, medium, hard}

  docker build completes without error          ✓ Exit code 0

  HF Space URL returns 200 on ping              ✓ Server live

  openenv.yaml exists in repo root              ✓ File present

  Baseline script runs without error            ✓ All 3 scores logged
  -----------------------------------------------------------------------

**11. Reward Function Design**

Your reward function uses three tiers of partial credit. This is what
the judges mean by \'meaningful reward function with partial progress
signals\':

  ------------------------------------------------------------------------
  **Score**       **Condition**   **Meaning**
  --------------- --------------- ----------------------------------------
  0.99            All tests pass  Agent produced a correct fix

  0.5             Code runs, no   Partial fix --- compiles but wrong logic
                  crash           

  0.01            Crash or syntax Fix is completely broken
                  error           
  ------------------------------------------------------------------------

This is better than binary scoring and shows the judges you understand
RL reward shaping --- not just pass/fail.

**12. README.md Content**

Your README must include these sections to pass the automated doc check:

> \# DebugTraceEnv
>
> An OpenEnv RL environment where an AI agent receives a broken Python
>
> function and must produce a corrected version.
>
> \## Environment Description
>
> Agent observes: broken code, failing test, stack trace.
>
> Agent action: fixed_code (string containing corrected function).
>
> Grader: runs pytest on the fix, returns score 0.0--1.0.
>
> \## Action Space
>
> POST /step with body: {\"fixed_code\": \"\<python function as
> string\>\"}
>
> \## Observation Space
>
> POST /reset returns: {task_id, description, broken_code, stack_trace,
> instruction}
>
> \## Tasks
>
> \- easy: Fix a syntax or runtime error
>
> \- medium: Fix a logic bug
>
> \- hard: Fix an algorithmic error
>
> \## Setup
>
> pip install -r requirements.txt
>
> python main.py
>
> \## Docker
>
> docker build -t debugtrace-env .
>
> docker run -p 7860:7860 debugtrace-env
>
> \## Baseline
>
> python baseline.py

**13. Submission Checklist**

Deadline: 7 April 2026, 11:59 PM IST

-   Push all files to GitHub (public repo)

-   Deploy Docker container to HuggingFace Spaces

-   Paste your HF Spaces URL in the submission form on the hackathon
    dashboard

-   Verify your URL responds to GET / with a 200 before submitting

The submission form asks for your HF Spaces URL only. Everything else is
validated automatically from that URL.

*DebugTraceEnv --- Build Specification*

*Scaler × Meta/PyTorch OpenEnv Hackathon · April 2026*
