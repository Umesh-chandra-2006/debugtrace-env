import subprocess, tempfile, os, json
from tasks import TASKS

class DebugTraceEnv:
    def __init__(self):
        self.current_task = None
        self.episode_done = False
        self.last_score = None

    def reset(self, task_id='easy'):
        task = next((t for t in TASKS if t['id'] == task_id), TASKS[0])
        self.current_task = task
        self.episode_done = False
        self.last_score = None
        return {
            'task_id': task['id'],
            'description': task['description'],
            'broken_code': task['broken_code'],
            'stack_trace': task['stack_trace'],
            'instruction': 'Return a fixed version of the function in fixed_code field'
        }

    def step(self, action: dict):
        if self.episode_done:
            return {'error': 'Episode done. Call /reset first.'}
        fixed_code = action.get('fixed_code', '')
        score = self._grade(fixed_code)
        self.last_score = score
        self.episode_done = True
        return {
            'reward': score,
            'done': True,
            'score': score,
            'passed': score >= 0.99
        }

    def state(self):
        return {
            'task_id': self.current_task['id'] if self.current_task else None,
            'episode_done': self.episode_done,
            'last_score': self.last_score
        }

    def _grade(self, fixed_code):
        task = self.current_task
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = os.path.join(tmpdir, 'solution.py')
            test_file = os.path.join(tmpdir, 'test_solution.py')
            with open(code_file, 'w') as f:
                f.write(fixed_code)
            with open(test_file, 'w') as f:
                f.write('from solution import *\n')
                f.write(task['test_code'])
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-q', '--tb=no'],
                capture_output=True, text=True, cwd=tmpdir, timeout=10
            )
            
            # Extract passed and failed counts from pytest output
            import re
            passed_match = re.search(r'(\d+) passed', result.stdout)
            failed_match = re.search(r'(\d+) failed', result.stdout)
            
            if passed_match:
                passed = int(passed_match.group(1))
                failed = int(failed_match.group(1)) if failed_match else 0
                total = passed + failed
                
                if total > 0:
                    # Calculate score as percentage of tests passed, scaled to (0, 1)
                    percentage = passed / total
                    # Map [0, 1] to (0.01, 0.98) 
                    score = 0.01 + (percentage * 0.97)
                    # Round to 2 decimal places to avoid floating point issues
                    return round(score, 2)
                    
            elif result.returncode == 0:
                return 0.5  # compiled, no crash, but no tests
            
            return 0.01
