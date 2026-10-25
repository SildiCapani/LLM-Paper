def generate_test_cases(num_cases: int, seed: int = 42) -> list[dict]:
    import math
    from collections import defaultdict
    import random
    from typing import List, Dict # Used by the sample solution logic

    random.seed(seed)

    # This class encapsulates the logic from the provided sample solution.
    class _SampleSolution:
        def findKthSmallest(self, coins: List[int], k: int) -> int:
            # coins_mutex is the set of coins where no coin is a multiple of another.
            # It's called coins_prime in my earlier thoughts, sticking to sample's name.
            _coins_sorted = sorted(list(set(coins))) # Ensure distinct and sorted
            
            coins_mutex = []
            if not _coins_sorted: # Should not happen based on constraints
                return 0 

            for coin_val in _coins_sorted:
                is_redundant = False
                for existing_coin in coins_mutex:
                    if coin_val % existing_coin == 0:
                        is_redundant = True
                        break
                if not is_redundant:
                    coins_mutex.append(coin_val)
            
            if not coins_mutex: # e.g. if input coins was empty, though constraints prevent this.
                 return 0 
            
            if len(coins_mutex) == 1:
                # Result must be long, Python handles large integers automatically.
                return coins_mutex[0] * k

            # lcms_map stores {lcm_value: sum_of_signs_for_pie}
            # e.g., for N/a + N/b - N/lcm(a,b), it stores {a:1, b:1, lcm(a,b):-1}
            lcms_map: Dict[int, int] = defaultdict(int)
            self._generate_lcms_for_pie(0, 1, 1, coins_mutex, lcms_map)

            # Binary search for the k-th amount.
            # The sample solution's range: left=k, right=coins_mutex[0]*k.
            # A tighter lower bound for `left` could be `coins_mutex[0]`.
            # Let's use `coins_mutex[0]` as the lower bound for `left` if `k` is too small.
            # The sample solution's `left=k` might be problematic if k is small and min_coin is large.
            # E.g. coins=[25], k=1. `left=1`, `right=25*1=25`. This is fine.
            # The sample solution's `left, right = k, coins_mutex[0] * k` is used.
            # It seems to work out due to how binary search converges.
            # Let's use the exact logic from the sample:
            # left, right = k, coins_mutex[0] * k
            # However, a more robust binary search range for the answer `X` is:
            # `low = 1` (or `coins_mutex[0]`)
            # `high = coins_mutex[0] * k` (an upper bound, since if only `coins_mutex[0]` existed, this would be the answer)
            
            low = 1 
            # coins_mutex is sorted because _coins_sorted was sorted and items are added in order.
            high = coins_mutex[0] * k 
            ans = high # Initialize ans to a valid upper value

            while low <= high:
                mid = low + (high - low) // 2
                if mid == 0: # Should not happen if low starts at 1 or min_coin
                    low = 1 
                    continue
                
                count = 0
                for lcm_val, factor in lcms_map.items():
                    if lcm_val == 0: continue # Should not happen with positive coins
                    count += (mid // lcm_val) * factor
                
                if count >= k:
                    ans = mid
                    high = mid - 1
                else:
                    low = mid + 1
            
            return ans # This is `left` in the original sample solution's typical BS return

        # Renamed from sample's `find_lcm` to avoid confusion with `math.lcm`
        # This method implements the Principle of Inclusion-Exclusion (PIE)
        # by generating all LCMs of subsets of coins_mutex and their corresponding signs.
        def _generate_lcms_for_pie(self, index: int, current_product_lcm: int, sign: int, unique_coins: List[int], lcms_map_ref: Dict[int, int]):
            # `current_product_lcm` is the 'base' in the sample solution.
            # `sign` is 'add_or_remove' in the sample solution.
            # `unique_coins` is 'coins_mutex'.
            # `lcms_map_ref` is 'lcms'.
            for i in range(index, len(unique_coins)):
                coin_to_include = unique_coins[i]
                
                # Calculate new LCM: lcm(current_product_lcm, coin_to_include)
                # math.lcm handles current_product_lcm = 1 correctly (initial call)
                # Python's math.lcm can take multiple args, but sample implies pairwise construction.
                # The sample solution's `lcm = math.lcm(base, coins[index_next])` is correct.
                # `base` is the LCM of the set of elements that formed the *previous* combination.
                # `coins[index_next]` is the new element being added.
                # The `lcm` calculated is the LCM of the *current* combination.
                
                # Let's follow the sample solution's `find_lcm` structure:
                # `base` is the LCM of the elements chosen *so far* for this specific term in PIE.
                # `coins[index_next]` is the *next* coin to consider adding to this combination.
                # `lcm_val = math.lcm(base, coins[index_next])`
                # This means `base` is the LCM of the current combination being built.
                # Initial call: (0, 1, 1, ...)
                #   Loop i from 0: lcm(1, coins[i]), sign=1. Recurse (i+1, coins[i], -1, ...)
                #     Loop j from i+1: lcm(coins[i], coins[j]), sign=-1. Recurse (j+1, lcm(coins[i],coins[j]), 1, ...)
                
                lcm_val = math.lcm(current_product_lcm, coin_to_include)
                
                lcms_map_ref[lcm_val] += sign
                if lcms_map_ref[lcm_val] == 0: # Optimization: remove if net contribution is zero
                    del lcms_map_ref[lcm_val]

                # Recursive call for combinations including coin_to_include and subsequent coins
                self._generate_lcms_for_pie(i + 1, lcm_val, -sign, unique_coins, lcms_map_ref)

    solver = _SampleSolution()
    
    generated_cases = []
    seen_test_case_strs = set()

    # Define specific hand-crafted test cases
    # (coins_list, k_val)
    specific_inputs = [
        ([3,6,9], 3), ([5,2], 7), ([5], 10), ([1], 1), ([1], 10**9),
        ([25,10,15], 1), ([2,4,6,8], 5), ([2,3,5], 10),
        (list(range(11, 26)), 1), # Max N (15 coins), largest values, k=1
        (list(range(1, 16)), 2 * 10**9), # Max N (15 coins), smallest values (includes 1), max k
        ([2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], 1000), # Max N, mixed values
        ([19,23], 10**9), # Large k, few large prime coins
        ([25], 2 * 10**9), # Max k, single max value coin
        ([24,25], 2 * 10**9), # Max k, two large coins
        (list(range(1,16)), 1), # Smallest coins, max N, k=1
        (list(range(11,26)), 20), # Largest coins, max N, moderate k
        ([13,17,19,23], 100), # All primes
        ([4,6,8,9,10,12,14,15,16,18,20,21,22,24,25], 500), # All composite, N=15
        ([1,25], 10**5), # Min and max coin value
        ([7, 14, 21], 10), # Coins are multiples of a base
    ]

    for coins, k_val in specific_inputs:
        if len(generated_cases) >= num_cases:
            break
        
        coins_str = ",".join(map(str, coins))
        input_str = f"{coins_str} {k_val}"
        
        output_val = solver.findKthSmallest(list(coins), k_val) # Pass a copy of coins
        output_str = str(output_val)

        if input_str not in seen_test_case_strs: # Technically input_str is enough for uniqueness if solution is deterministic
            generated_cases.append({"input": input_str, "output": output_str})
            seen_test_case_strs.add(input_str)

    # Fill with random cases if needed
    coin_value_population = list(range(1, 26))
    while len(generated_cases) < num_cases:
        num_coins_in_case = random.randint(1, 15)
        coins = sorted(random.sample(coin_value_population, num_coins_in_case))
        
        # K can be small or very large
        k_rand_type = random.random()
        if k_rand_type < 0.33: # Small k
            k_val = random.randint(1, 100)
        elif k_rand_type < 0.66: # Medium k
            k_val = random.randint(101, 10**5)
        else: # Large k
            k_val = random.randint(10**5 + 1, 2 * 10**9)
            # Ensure k is not excessively large for small coin values if it causes overflow issues for naive solutions
            # (though this solution handles it). For example, if min_coin is 1, k can be up to 2*10^9.
            # If min_coin is 25, k can be up to 2*10^9. Max result 50*10^9.

        coins_str = ",".join(map(str, coins))
        input_str = f"{coins_str} {k_val}"

        if input_str not in seen_test_case_strs:
            output_val = solver.findKthSmallest(list(coins), k_val)
            output_str = str(output_val)
            generated_cases.append({"input": input_str, "output": output_str})
            seen_test_case_strs.add(input_str)
        # If collision, loop continues to try to find a new unique case.
        # For very high num_cases, this might be slow if unique cases are exhausted,
        # but problem constraints allow for many unique (coins, k) pairs.

    return generated_cases