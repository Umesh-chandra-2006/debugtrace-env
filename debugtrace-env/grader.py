# Grader module - provides grading interface
# The main grading logic is in env.py under DebugTraceEnv._grade()

from env import DebugTraceEnv

def grade_submission(task_id, fixed_code):
    """
    Grade a submission for a given task.
    
    Args:
        task_id: The task ID ('easy', 'medium', or 'hard')
        fixed_code: The fixed code as a string
        
    Returns:
        dict with 'score' (0.0-1.0) and 'passed' (bool) fields
    """
    env = DebugTraceEnv()
    env.reset(task_id)
    result = env.step({'fixed_code': fixed_code})
    return {
        'score': result.get('score', 0.0),
        'passed': result.get('passed', False)
    }
