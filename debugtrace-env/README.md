---
title: DebugTraceEnv
emoji: 🐛
colorFrom: blue
colorTo: green
sdk: docker
app_file: main.py
pinned: false
---

# DebugTraceEnv

A reinforcement learning environment for debugging broken Python functions.

## Overview

DebugTraceEnv is an RL environment where an AI agent receives:
- A broken Python function with a bug
- A failing test suite
- A stack trace

The agent must produce a corrected version of the function. The grader runs the fix against the test suite and returns a score from 0.0 to 1.0.

## Project Structure

```
debugtrace-env/
├── main.py           # FastAPI app with all endpoints
├── env.py            # Core environment logic
├── tasks.py          # 3 task definitions (easy, medium, hard)
├── grader.py         # Grader logic (runs pytest)
├── openenv.yaml      # OpenEnv spec manifest
├── baseline.py       # Baseline agent script
├── Dockerfile        # Docker build file
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Tasks

### Task 1: Easy - Syntax/Runtime Error
Fix a simple runtime error like IndexError from off-by-one range bug.

### Task 2: Medium - Logic Bug
Fix a logic mistake that causes incorrect output without crashing.

### Task 3: Hard - Algorithmic Error
Fix a deeper algorithmic bug or incorrect algorithm implementation.

## API Endpoints

- `POST /reset` - Reset environment and start a task
  ```json
  {"task_id": "easy"}
  ```

- `POST /step` - Submit a fixed code solution
  ```json
  {"fixed_code": "def sum_list(nums):\n    ..."}
  ```

- `GET /state` - Get current environment state

- `GET /tasks` - List all available tasks

- `POST /grader` - Grade a fixed code submission
  ```json
  {"fixed_code": "def sum_list(nums):\n    ..."}
  ```

- `POST /baseline` - Run baseline agent with correct answers

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The server will start at `http://localhost:7860`

3. Test with baseline:
```bash
python baseline.py
```

## Docker Deployment

1. Build the image:
```bash
docker build -t debugtrace-env .
```

2. Run the container:
```bash
docker run -p 7860:7860 debugtrace-env
```

## Submission

Deploy to Hugging Face Spaces:
1. Create a new Space on huggingface.co
2. Push this repository to the Space
3. Space will automatically build and deploy the Docker image
4. Share your Space URL with judges

## OpenEnv Specification

See `openenv.yaml` for the formal specification including:
- Task definitions and difficulty levels
- API endpoint specifications
- Environment metadata

## Baseline Performance

The baseline agent achieves 1.0 (perfect) score on all tasks by submitting hardcoded correct fixes. This validates that the grader works correctly.

## Development

To modify tasks or add new grading logic:
- Edit `tasks.py` to add/modify tasks
- Edit `env.py` to change grading logic
- Restart the server to apply changes
