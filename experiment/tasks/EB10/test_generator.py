def generate_test_cases(num_cases: int, seed: int = 42) -> list:
    import random
    random.seed(seed)

    def sample_solution(wordsContainer, wordsQuery):
        trie = {}
        for i, word in enumerate(wordsContainer):
            size = len(word)
            t = trie
            for c in word[::-1]:
                if '#' in t:
                    if len(wordsContainer[t['#']]) > size:
                        t['#'] = i
                else:
                    t['#'] = i
                if c not in t:
                    t[c] = {}
                t = t[c]
            if '#' in t:
                if len(wordsContainer[t['#']]) > size:
                    t['#'] = i
            else:
                t['#'] = i
        res = []
        for word in wordsQuery:
            t = trie
            found = False
            for c in word[::-1]:
                if c not in t:
                    res.append(t['#'])
                    found = True
                    break
                t = t[c]
            if not found:
                res.append(t['#'])
        return res

    tests = []
    fixed_cases = [
        (["a"], ["a"]),
        (["abcd", "bcd", "xbcd"], ["cd", "bcd", "xyz"]),
        (["abcdefgh", "poiuygh", "ghghgh"], ["gh", "acbfgh", "acbfegh"]),
        (["abc", "bbc", "cbc"], ["bc", "c", "ab"]),
        (["abzz", "zbzz", "cbzz"], ["zz", "zz", "zz"]),
    ]
    
    for wc, wq in fixed_cases:
        input_serialized = ",".join(wc) + "\n" + ",".join(wq)
        expected_output = sample_solution(wc, wq)
        output_serialized = ",".join(str(x) for x in expected_output)
        tests.append({"input": input_serialized, "output": output_serialized})
        if len(tests) >= num_cases:
            return tests[:num_cases]
    
    while len(tests) < num_cases:
        n_container = random.randint(1, 10)
        n_query = random.randint(1, 10)
        def random_word():
            length = random.randint(1, 10)
            return "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(length))
        wordsContainer = [random_word() for _ in range(n_container)]
        wordsQuery = [random_word() for _ in range(n_query)]
        input_serialized = ",".join(wordsContainer) + "\n" + ",".join(wordsQuery)
        expected_output = sample_solution(wordsContainer, wordsQuery)
        output_serialized = ",".join(str(x) for x in expected_output)
        tests.append({"input": input_serialized, "output": output_serialized})
    return tests[:num_cases]