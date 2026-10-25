def generate_test_cases(num_cases: int, seed: int = 42) -> list:
    import random
    from collections import Counter
    random.seed(seed)

    # Sample solution adapted from provided sample solution.
    def sample_solution(power):
        cnt = Counter(power)
        keys = sorted(cnt.keys())
        n = len(keys)
        dp = [0]*(n+1)
        dp[1] = cnt[keys[0]] * keys[0]
        if n == 1:
            return dp[1]
        if keys[1] - keys[0] > 2:
            dp[2] = dp[1] + cnt[keys[1]] * keys[1]
        else:
            dp[2] = max(cnt[keys[1]] * keys[1], cnt[keys[0]] * keys[0])
        for i in range(2, n):
            if keys[i] - keys[i-1] > 2:
                dp[i+1] = dp[i] + cnt[keys[i]] * keys[i]
            elif keys[i] - keys[i-2] > 2:
                dp[i+1] = max(dp[i], dp[i-1] + cnt[keys[i]] * keys[i])
            else:
                dp[i+1] = max(dp[i], dp[i-2] + cnt[keys[i]] * keys[i])
        return dp[-1]

    test_cases = []
    for _ in range(num_cases):
        # Randomly choose a test case type.
        case_type = random.randint(0, 5)
        if case_type == 0:
            # All elements are the same.
            val = random.randint(1, 50)
            length = random.randint(1, 20)
            power_list = [val] * length
        elif case_type == 1:
            # Sorted increasing order.
            length = random.randint(1, 20)
            power_list = sorted(random.randint(1, 50) for _ in range(length))
        elif case_type == 2:
            # Sorted decreasing order.
            length = random.randint(1, 20)
            power_list = sorted((random.randint(1, 50) for _ in range(length)), reverse=True)
        elif case_type == 3:
            # Random unsorted list.
            length = random.randint(1, 20)
            power_list = [random.randint(1, 50) for _ in range(length)]
        elif case_type == 4:
            # Minimal length edge case.
            power_list = [random.randint(1, 50)]
        elif case_type == 5:
            # Mixed values with potential gaps.
            length = random.randint(1, 20)
            power_list = [random.randint(1, 10) if random.random() < 0.5 else random.randint(40, 50)
                          for _ in range(length)]
        # Serialize input as a comma-separated string.
        serialized_input = ",".join(map(str, power_list))
        expected_output = str(sample_solution(power_list))
        test_cases.append({"input": serialized_input, "output": expected_output})
    return test_cases