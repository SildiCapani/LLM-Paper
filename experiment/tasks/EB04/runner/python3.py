# Helper function 'pairwise' used by the Solution class.
==Code Submission==
# It relies on the 'itertools' module being available from auto-injected imports.
def pairwise(iterable):
    # 'itertools' is auto-injected, so 'itertools.tee' can be used.
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

==Code Submission==
# The Solution code (including MOD, m1, m2, fac, ifac, and the Solution class)
==Code Submission==

# Test runner logic for Python 3 starts here.
# The 'sys' module is auto-injected and available.

# Increase Python's recursion limit.
# This must be done after the 'fac' function is defined (via injection)
# but before it's called with a potentially large argument.
# Max N is 10^5. A limit like 105000 or 110000 should be safe.
sys.setrecursionlimit(110000) 

def deserialize_input(input_str: str) -> tuple[int, list[int]]:
    # Parses "n sick_val1,sick_val2,..."
    # Example: "5 0,4" -> n=5, sick=[0,4]
    parts = input_str.strip().split(' ', 1)
    n = int(parts[0])
    
    # Problem constraints: 1 <= sick.length <= n - 1.
    # So, parts[1] should always exist and contain comma-separated integers.
    sick_list_str = parts[1]
    # Robustly handle potential empty strings if split results in them (e.g. "1,,2")
    # though problem constraints on sick values likely prevent this.
    sick = [int(x) for x in sick_list_str.split(',') if x.strip()]
    return n, sick

def serialize_output(result: int) -> str:
    # Output is a single integer, serialized as a string.
    return str(result)

# Main execution block of the test runner.
# sys.stdin is available from auto-injected 'import sys'.
raw_input_line = sys.stdin.read().strip() 

n_val, sick_val = deserialize_input(raw_input_line)

# The Solution class is defined from the injected code.
solution_instance = Solution()
result_ans = solution_instance.numberOfSequence(n_val, sick_val)

print(serialize_output(result_ans))