def generate_test_cases(num_cases: int, seed: int = 42) -> list[dict]:
    import random
    from collections import deque
    random.seed(seed)
    
    # Sample solution adapted from the provided implementation.
    def sample_solution(prices):
        prices = [0] + prices  # add dummy zero at the beginning
        n = len(prices)
        if n <= 3:
            return prices[1]
        dp = [0] * n
        dp[1] = prices[1]
        dp[2] = prices[1]
        q = deque([2])
        for i in range(3, n):
            while q and q[0] * 2 < i:
                q.popleft()
            dp[i] = dp[i - 1] + prices[i]
            if q:
                dp[i] = min(dp[i], dp[q[0] - 1] + prices[q[0]])
            while q and (dp[q[-1] - 1] + prices[q[-1]] >= dp[i - 1] + prices[i]):
                q.pop()
            q.append(i)
        return dp[-1]
    
    # Predefined test cases covering various scenarios.
    predefined = [
        [3, 1, 2],                               # Example 1
        [1, 10, 1, 1],                            # Example 2
        [26, 18, 6, 12, 49, 7, 45, 45],            # Example 3
        [5],                                      # Single element edge case
        list(range(1, 11)),                       # Sorted ascending list
        list(range(10, 0, -1)),                    # Sorted descending list
        [2] * 10                                  # Repeated elements
    ]
    
    tests = []
    # Use predefined test cases first.
    for prices in predefined:
        if len(tests) >= num_cases:
            break
        inp = ",".join(map(str, prices))
        expected = sample_solution(prices)
        tests.append({"input": inp, "output": str(expected)})
    
    # Generate additional random test cases if needed.
    while len(tests) < num_cases:
        # With 20% chance, generate a stress test case.
        if random.random() < 0.2:
            n = random.randint(500, 1000)
            low, high = 1, 10**5
        else:
            n = random.randint(1, 50)
            low, high = 1, 100
        prices = [random.randint(low, high) for _ in range(n)]
        inp = ",".join(map(str, prices))
        expected = sample_solution(prices)
        tests.append({"input": inp, "output": str(expected)})
    
    return tests