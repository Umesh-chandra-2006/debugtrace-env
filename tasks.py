TASKS = [
    {
        'id': 'easy',
        'description': 'Fix a syntax or obvious runtime error',
        'difficulty': 'easy',
        'broken_code': '''def sum_list(nums):
    total = 0
    for i in range(len(nums) + 1):  # bug: +1 causes IndexError
        total += nums[i]
    return total''',
        'test_code': '''def test_sum_list_basic():
    assert sum_list([1, 2, 3]) == 6

def test_sum_list_empty():
    assert sum_list([]) == 0''',
        'stack_trace': 'IndexError: list index out of range at line 4 in sum_list'
    },
    {
        'id': 'medium',
        'description': 'Fix a logic bug producing wrong output',
        'difficulty': 'medium',
        'broken_code': '''def is_palindrome(s):
    return s == s[1:]  # bug: should be s[::-1]''',
        'test_code': '''def test_is_palindrome_true():
    assert is_palindrome('racecar') == True

def test_is_palindrome_false():
    assert is_palindrome('hello') == False''',
        'stack_trace': 'Logic error: function returns incorrect boolean'
    },
    {
        'id': 'hard',
        'description': 'Fix a multi-step algorithmic error',
        'difficulty': 'hard',
        'broken_code': '''def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        diff = target - n
        if diff in seen:
            return [i, seen[diff]]  # bug: indices reversed
        seen[n] = i
    return []''',
        'test_code': '''def test_two_sum_case1():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]

def test_two_sum_case2():
    assert two_sum([3, 2, 4], 6) == [1, 2]''',
        'stack_trace': 'Logic error: incorrect index order returned'
    }
]
