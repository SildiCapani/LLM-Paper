def generate_test_cases(num_cases: int, seed: int = 42) -> list:
    import random
    from collections import Counter
    random.seed(seed)

    def expected_solution(s: str, queries: list) -> list:
        n = len(s)
        q = len(queries)
        s1 = s[: n // 2]
        s2 = s[n // 2:][::-1]
        if Counter(s1) != Counter(s2):
            return [False] * q
        queries_transformed = []
        for a, b, c, d in queries:
            queries_transformed.append([a, b, n - 1 - d, n - 1 - c])
        n2 = n // 2
        left = [-1] * n2
        l = -1
        for i in range(n2):
            if s1[i] == s2[i]:
                if l == -1:
                    l = i
            else:
                if l != -1:
                    for j in range(l, i):
                        left[j] = i - 1
                    l = -1
        if l != -1:
            for j in range(l, n2):
                left[j] = n2 - 1

        cnt1 = [[0] * 26]
        curr = [0] * 26
        for i in range(n2):
            curr[ord(s1[i]) - ord('a')] += 1
            cnt1.append(curr[:])
        cnt2 = [[0] * 26]
        curr = [0] * 26
        for i in range(n2):
            curr[ord(s2[i]) - ord('a')] += 1
            cnt2.append(curr[:])
        result = []
        for a, b, c, d in queries_transformed:
            flag = True
            if a > c:
                a, b, c, d = c, d, a, b
                flag = False
            if b < c - 1:
                if left[b + 1] >= c - 1 and (a - 1 < 0 or left[0] >= a - 1) and (d == n2 - 1 or left[d + 1] == n2 - 1):
                    curr_list = [0] * 26
                    total = [0] * 26
                    possible = True
                    for i in range(26):
                        curr_list[i] = cnt2[b + 1][i] - cnt2[a][i]
                        total[i] = cnt1[b + 1][i] - cnt1[a][i]
                        if total[i] < curr_list[i]:
                            possible = False
                            break
                    result.append(possible)
                else:
                    result.append(False)
            elif b >= d:
                if (a - 1 < 0 or left[0] >= a - 1) and (b == n2 - 1 or left[b + 1] == n2 - 1):
                    result.append(True)
                else:
                    result.append(False)
            else:
                if (a - 1 < 0 or left[0] >= a - 1) and (d == n2 - 1 or left[d + 1] == n2 - 1):
                    curr_list = [0] * 26
                    total = [0] * 26
                    if flag:
                        possible = True
                        for i in range(26):
                            curr_list[i] = cnt2[c][i] - cnt2[a][i]
                            total[i] = cnt1[b + 1][i] - cnt1[a][i]
                            if total[i] < curr_list[i]:
                                possible = False
                                break
                        result.append(possible)
                    else:
                        possible = True
                        for i in range(26):
                            curr_list[i] = cnt1[c][i] - cnt1[a][i]
                            total[i] = cnt2[b + 1][i] - cnt2[a][i]
                            if total[i] < curr_list[i]:
                                possible = False
                                break
                        result.append(possible)
                else:
                    result.append(False)
        return result

    def serialize_input(s: str, queries: list) -> str:
        query_strs = []
        for q in queries:
            query_strs.append(",".join(str(x) for x in q))
        return s + "\n" + ";".join(query_strs)

    def serialize_output(result: list) -> str:
        return ",".join("true" if x else "false" for x in result)

    fixed_tests = []
    fixed_tests.append(("aa", [[0, 0, 1, 1]]))
    fixed_tests.append(("abba", [[0, 0, 2, 2]]))
    fixed_tests.append(("abcc", [[0, 0, 2, 3]]))
    fixed_tests.append(("abcabc", [[1, 1, 3, 5], [0, 2, 5, 5]]))
    fixed_tests.append(("abbcdecbba", [[0, 2, 7, 9]]))
    fixed_tests.append(("acbcab", [[1, 2, 4, 5]]))
    
    test_cases = []
    count_fixed = min(num_cases, len(fixed_tests))
    for i in range(count_fixed):
        s, queries = fixed_tests[i]
        expected = expected_solution(s, queries)
        inp = serialize_input(s, queries)
        out = serialize_output(expected)
        test_cases.append({"input": inp, "output": out})
    for _ in range(num_cases - count_fixed):
        n = random.choice(range(2, 21, 2))
        s = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=n))
        num_queries = random.randint(1, max(1, n // 4))
        queries = []
        for _ in range(num_queries):
            a = random.randint(0, n // 2 - 1)
            b = random.randint(a, n // 2 - 1)
            c = random.randint(n // 2, n - 1)
            d = random.randint(c, n - 1)
            queries.append([a, b, c, d])
        expected = expected_solution(s, queries)
        inp = serialize_input(s, queries)
        out = serialize_output(expected)
        test_cases.append({"input": inp, "output": out})
    return test_cases