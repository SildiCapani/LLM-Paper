def generate_test_cases(num_cases: int, seed: int = 42) -> list:
    import random
    random.seed(seed)
    
    # Helper function using the provided sample solution to compute expected output.
    def sample_solution(start: int, finish: int, limit: int, s: str) -> int:
        startStr, finishStr = str(start - 1), str(finish)
        def calculate(num: str) -> int:
            if len(num) < len(s):
                return 0
            if len(num) == len(s):
                return 1 if num >= s else 0
            lengthDiff = len(num) - len(s)
            substr = num[lengthDiff:]
            ans = 0
            for idx in range(lengthDiff):
                digit = ord(num[idx]) - ord('0')
                if limit < digit:
                    ans += (limit + 1) ** (lengthDiff - idx)
                    return ans
                ans += digit * ((limit + 1) ** (lengthDiff - 1 - idx))
            if substr >= s:
                ans += 1
            return ans
        return calculate(finishStr) - calculate(startStr)
    
    test_cases = []
    
    # Fixed test cases from examples and additional edge cases:
    fixed_cases = [
        (1, 6000, 4, "124"),
        (15, 215, 6, "10"),
        (1000, 2000, 4, "3000"),
        (1, 10, 9, "1"),
        (10, 100, 5, "25")
    ]
    
    for case in fixed_cases:
        if len(test_cases) >= num_cases:
            break
        start_val, finish_val, limit_val, s_val = case
        inp = f"{start_val},{finish_val},{limit_val},{s_val}"
        out = str(sample_solution(start_val, finish_val, limit_val, s_val))
        test_cases.append({"input": inp, "output": out})
    
    # Generate additional random test cases if needed.
    while len(test_cases) < num_cases:
        # Pick start within a wide range.
        start_val = random.randint(1, 10**12)
        # Ensure finish is at least start and does not exceed 10^15.
        finish_val = random.randint(start_val, min(start_val + 10**6, 10**15))
        limit_val = random.randint(1, 9)
        # Maximum length of s is the number of digits in finish.
        max_len = len(str(finish_val))
        length_s = random.randint(1, max_len)
        # First digit from 1 to limit_val (avoid leading zero), subsequent digits from 0 to limit_val.
        first_digit = str(random.randint(1, limit_val))
        if length_s == 1:
            s_val = first_digit
        else:
            s_val = first_digit + "".join(str(random.randint(0, limit_val)) for _ in range(length_s - 1))
        inp = f"{start_val},{finish_val},{limit_val},{s_val}"
        out = str(sample_solution(start_val, finish_val, limit_val, s_val))
        test_cases.append({"input": inp, "output": out})
    
    return test_cases