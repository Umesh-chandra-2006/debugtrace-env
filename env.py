import subprocess, tempfile, os
from tasks import TASKS

class DebugTraceEnv:
    def __init__(self):
        self.current_task = None
        self.episode_done = False
        self.last_score = None

    def _get_observation(self):
        if not self.current_task:
            return None
        return {
            'task_id': self.current_task['id'],
            'description': self.current_task['description'],
            'broken_code': self.current_task['broken_code'],
            'stack_trace': self.current_task['stack_trace'],
            'instruction': 'Return a fixed version of the function in fixed_code field'
        }

    def reset(self, task_id='easy'):
        task = next((t for t in TASKS if t['id'] == task_id), TASKS[0])
        self.current_task = task
        self.episode_done = False
        self.last_score = None
        return {
            "observation": self._get_observation()
        }

    def step(self, action: dict):
        if self.episode_done:
            return {'error': 'Episode done. Call /reset first.'}
        fixed_code = action.get('fixed_code', '')
        score = self._grade(fixed_code)
        self.last_score = score
        self.episode_done = True
        return {
            "observation": self._get_observation(),
            "reward": score,
            "done": True,
            "info": {
                "score": score,
                "passed": score >= 0.99
            }
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

            import re
            passed_match = re.search(r'(\d+) passed', result.stdout)
            failed_match = re.search(r'(\d+) failed', result.stdout)

            if passed_match:
                passed = int(passed_match.group(1))
                failed = int(failed_match.group(1)) if failed_match else 0
                total = passed + failed
                
                if passed == total and total > 0:
                    return 0.99
                elif total > 0:
                    # Scale partial passing fraction out of 0.98 maximum partial bound
                    score = 0.01 + ((passed / total) * 0.97)
                    return round(score, 2)
            elif result.returncode == 0:
                return 0.5  # compiled, no crash, but no tests passed
            
            return 0.01
