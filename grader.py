from env import DebugTraceEnv

def grade_submission(task_id, fixed_code):
    env = DebugTraceEnv()
    env.reset(task_id)
    result = env.step({'fixed_code': fixed_code})
    return {
        'score': result.get('score', 0.0),
        'passed': result.get('passed', False)
    }
