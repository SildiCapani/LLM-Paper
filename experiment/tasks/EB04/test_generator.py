def generate_test_cases(num_cases: int, seed: int = 42) -> list[dict]:
    import random
    from itertools import pairwise # For use in _calculate_expected_output

    # --- Start of adapted sample solution logic ---
    _MOD = 10**9 + 7
    _m1_memo = {}  # Memoization for factorial
    _m2_memo = {}  # Memoization for inverse factorial

    def _fac(n_val):
        if n_val < 0:
            # This case should ideally not be reached if inputs are valid.
            # Factorial is not defined for negative numbers.
            # Depending on problem context, could raise error or return specific value.
            # Given constraints, n_val will be non-negative.
            raise ValueError("Factorial of negative number")
        if n_val not in _m1_memo:
            if n_val == 0:
                _m1_memo[n_val] = 1
            else:
                _m1_memo[n_val] = (n_val * _fac(n_val - 1)) % _MOD
        return _m1_memo[n_val]

    def _ifac(n_val):
        if n_val not in _m2_memo:
            _m2_memo[n_val] = pow(_fac(n_val), -1, _MOD)
        return _m2_memo[n_val]

    def _calculate_expected_output(n: int, s: list[int]) -> int:
        # Constraints: 2 <= n <= 10^5, 1 <= sick.length <= n-1
        # s is sorted, 0 <= s[i] <= n-1
        
        if not s: # Should not happen due to sick.length >= 1
            return 0 
        
        uninfected_count = n - len(s)
        if uninfected_count < 0: # Should not happen if sick.length <= n
             # This case implies more sick people than total people, which is invalid.
             # Or, if sick has duplicates and len(s) is based on that. But sick has unique positions.
             raise ValueError("More sick people than total people or invalid sick list.")

        if uninfected_count == 0:
            # All people are initially sick, or no uninfected people left.
            # The infection sequence is empty. There's 1 way for an empty sequence.
            return 1
        
        res = _fac(uninfected_count)
        
        # Segment before the first sick person (indices 0 to s[0]-1)
        first_segment_len = s[0]
        res = (res * _ifac(first_segment_len)) % _MOD
        
        # Segment after the last sick person (indices s[-1]+1 to n-1)
        last_segment_len = n - s[-1] - 1
        res = (res * _ifac(last_segment_len)) % _MOD
        
        # Segments between consecutive sick people
        for prev_sick, curr_sick in pairwise(s):
            # Length of uninfected segment: (curr_sick - 1) - (prev_sick + 1) + 1 = curr_sick - prev_sick - 1
            gap_len = curr_sick - prev_sick - 1
            if gap_len > 0:
                res = (res * _ifac(gap_len)) % _MOD
                # For a segment of length k >= 1 between two infection sources,
                # there are 2^(k-1) ways to infect it.
                res = (res * pow(2, gap_len - 1, _MOD)) % _MOD
        return res
    # --- End of adapted sample solution logic ---

    rng = random.Random(seed)
    test_cases = []
    seen_cases = set() # To ensure unique test cases based on serialized input

    # Predefined specific cases for boundaries and examples
    # (n, sick_list)
    fixed_cases_data = [
        (5, [0, 4]),  # Example 1
        (4, [1]),    # Example 2
        (2, [0]),    # Min n, min sick_len, sick at start
        (2, [1]),    # Min n, min sick_len, sick at end
        (3, [1]),    # n=3, one sick in middle
        (3, [0, 2]),  # n=3, sick at ends, one uninfected in middle (gap_len=1)
        (7, [3]),    # Single sick person in middle
        (7, [0]),    # Single sick person at start
        (7, [6]),    # Single sick person at end
        (7, [0, 6]), # Sick at both ends, large middle gap
        (7, [2, 4]), # Sick in middle, gaps at ends and middle
        (7, [0, 1, 2, 3, 4, 5]), # n-1 sick, one uninfected at end
        (7, [1, 2, 3, 4, 5, 6]), # n-1 sick, one uninfected at start
        (7, [0, 2, 3, 4, 5, 6]), # n-1 sick, one uninfected in middle (gap of 1, s[0]=0)
        (7, [0, 1, 2, 4, 5, 6]), # n-1 sick, one uninfected in middle (gap of 1)
        (10, [0,1,2,3,4,5,6,7,8]), # n=10, sick_len=n-1
        (10, [1,2,3,4,5,6,7,8,9]), # n=10, sick_len=n-1
        (10, [0,9]), # n=10, sick at ends
        (10, [4,5]), # n=10, two adjacent sick in middle
        (20, [5,10,15]), # Multiple gaps
    ]
    
    # Max constraints for stress tests
    MAX_N_CONSTRAINED = 10**5

    # Add stress cases if num_cases is large enough
    if num_cases > len(fixed_cases_data):
        fixed_cases_data.extend([
            (MAX_N_CONSTRAINED, [0]), # Max N, sick at start
            (MAX_N_CONSTRAINED, [MAX_N_CONSTRAINED - 1]), # Max N, sick at end
            (MAX_N_CONSTRAINED, [MAX_N_CONSTRAINED // 2]), # Max N, sick in middle
            (MAX_N_CONSTRAINED, [0, MAX_N_CONSTRAINED - 1]), # Max N, sick at ends
            (MAX_N_CONSTRAINED, sorted(rng.sample(range(MAX_N_CONSTRAINED), min(100, MAX_N_CONSTRAINED-1) )) ), # Max N, 100 sick people
            (MAX_N_CONSTRAINED, list(range(MAX_N_CONSTRAINED - 1))), # Max N, N-1 sick people (0 to N-2)
            (MAX_N_CONSTRAINED, list(range(1, MAX_N_CONSTRAINED))), # Max N, N-1 sick people (1 to N-1)
        ])


    for n_val, sick_val in fixed_cases_data:
        if len(test_cases) >= num_cases:
            break
        
        sick_str_list = [str(x) for x in sick_val]
        input_str = f"{n_val} {','.join(sick_str_list)}"

        if input_str not in seen_cases:
            output_val = _calculate_expected_output(n_val, sick_val)
            output_str = str(output_val)
            
            test_cases.append({"input": input_str, "output": output_str})
            seen_cases.add(input_str)

    # Generate random cases until num_cases is met
    MAX_N_FOR_RANDOM = 1000 # General random cases up to this N
    
    while len(test_cases) < num_cases:
        rand_mode = rng.random()
        n_val = 0
        
        if rand_mode < 0.6: # Smaller N values, higher probability
            n_val = rng.randint(2, MAX_N_FOR_RANDOM)
        elif rand_mode < 0.9: # Medium N values
            n_val = rng.randint(MAX_N_FOR_RANDOM + 1, MAX_N_CONSTRAINED // 10)
            if n_val < 2 : n_val = MAX_N_FOR_RANDOM # ensure it's larger
        else: # Large N values (stress)
            n_val = rng.randint(MAX_N_CONSTRAINED // 10 + 1, MAX_N_CONSTRAINED)
            if n_val < 2 : n_val = MAX_N_CONSTRAINED // 2 # ensure it's large

        n_val = max(2, n_val) # Ensure n is at least 2

        min_sick_len = 1
        max_sick_len = n_val - 1
        
        sick_len = 1
        if max_sick_len > min_sick_len: # if n_val > 2
            # Varied sick_len: small, large, or proportional
            len_rand_mode = rng.random()
            if len_rand_mode < 0.33: # Small sick_len
                sick_len = rng.randint(min_sick_len, min(max_sick_len, 10))
            elif len_rand_mode < 0.66: # Large sick_len (n-k for small k)
                k = rng.randint(1, min(max_sick_len, 10)) # k is number of uninfected people + 1
                sick_len = max(min_sick_len, max_sick_len - k + 1)
            else: # Random sick_len in range
                 sick_len = rng.randint(min_sick_len, max_sick_len)
        
        sick_len = max(min_sick_len, min(sick_len, max_sick_len)) # clamp to valid range

        sick_val = sorted(rng.sample(range(n_val), sick_len))
        
        sick_str_list = [str(x) for x in sick_val]
        input_str = f"{n_val} {','.join(sick_str_list)}"

        if input_str not in seen_cases:
            output_val = _calculate_expected_output(n_val, sick_val)
            output_str = str(output_val)
            
            test_cases.append({"input": input_str, "output": output_str})
            seen_cases.add(input_str)
            
    return test_cases