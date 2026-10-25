def generate_test_cases(num_cases: int, seed: int = 42) -> list[dict]:
    import random
    random.seed(seed)
    
    # Helper: sample solution from provided sample code
    def sample_solution(nums):
        n = len(nums)
        digitSize = len(str(nums[0]))
        ans = 0
        denominator = 1
        for _ in range(digitSize):
            count = [0] * 10
            for num in nums:
                count[(num // denominator) % 10] += 1
            ans += sum(freq * (n - freq) for freq in count)
            denominator *= 10
        return ans // 2

    # Serialization helpers
    def serialize_input(nums):
        # Simple comma-separated serialization
        return ",".join(str(num) for num in nums)

    def serialize_output(result):
        # Simply output the integer result as string
        return str(result)
    
    test_cases = []
    # Predefined (base) test cases covering boundaries and core functionality.
    base_cases = [
        [1, 2],                    # minimal one-digit case
        [10, 10, 10, 10],          # all-equal two-digit case (expected 0)
        [13, 23, 12],              # example from problem description (expected 4)
        [123, 321, 213]            # three-digit case with mixed digits
    ]
    
    for nums in base_cases:
        if len(test_cases) >= num_cases:
            break
        # Ensure all numbers have the same number of digits.
        str_len = len(str(nums[0]))
        if any(len(str(num)) != str_len for num in nums):
            continue  # skip invalid case
        expected = sample_solution(nums)
        test_cases.append({
            "input": serialize_input(nums),
            "output": serialize_output(expected)
        })
    
    # Generate additional random test cases if needed.
    while len(test_cases) < num_cases:
        # Choose a random digit count between 1 and 9.
        digit_count = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
        lower = 10 ** (digit_count - 1)
        upper = 10 ** digit_count - 1
        n = random.randint(2, 10)  # array length between 2 and 10
        nums = [random.randint(lower, upper) for _ in range(n)]
        expected = sample_solution(nums)
        test_cases.append({
            "input": serialize_input(nums),
            "output": serialize_output(expected)
        })
        
    return test_cases