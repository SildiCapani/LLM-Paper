import random
from collections import defaultdict

def generate_test_cases(num_cases: int, seed: int = 42) -> list:
    random.seed(seed)
    test_cases = []

    # Helper: sample solution adapted from the provided sample
    def sample_solution(p, s):
        n = len(s)
        # Make a copy since we modify the parent list in DFS.
        p = p[:]
        res = [0] * n
        clds = defaultdict(list)
        for i in range(n):
            clds[p[i]].append(i)
        def dfs(i, anc):
            prv = anc.get(s[i])
            anc[s[i]] = i
            res[i] = 1
            for c in clds[i]:
                dfs(c, anc)
                res[p[c]] += res[c]
            anc[s[i]] = prv
            if prv is not None:
                p[i] = prv
        dfs(0, {})
        return res

    # Serialization helpers (simple string format)
    def serialize_input(p, s):
        # p as comma separated integers, then a space, then s.
        return ",".join(map(str, p)) + " " + s

    def serialize_output(result):
        return ",".join(map(str, result))

    fixed_tests = []
    # Boundary Case: single node tree.
    fixed_tests.append(([-1], "a"))
    # Sample Test Case 1
    fixed_tests.append(([-1, 0, 0, 1, 1, 1], "abaabc"))
    # Sample Test Case 2
    fixed_tests.append(([-1, 0, 4, 0, 1], "abbba"))

    # Generate additional random test cases if needed.
    for _ in range(num_cases - len(fixed_tests)):
        n = random.randint(2, 20)
        p = [-1]
        for i in range(1, n):
            p.append(random.randint(0, i - 1))
        # Create a random string s of length n from a few lowercase letters.
        s = "".join(random.choice("abcd") for _ in range(n))
        fixed_tests.append((p, s))

    # Use only the first num_cases test cases.
    for p, s in fixed_tests[:num_cases]:
        inp = serialize_input(p, s)
        expected = serialize_output(sample_solution(p, s))
        test_cases.append({"input": inp, "output": expected})
    return test_cases