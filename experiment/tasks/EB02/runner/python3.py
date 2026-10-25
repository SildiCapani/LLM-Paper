# Auto-injected: from typing import List, Dict, etc.
# No helper data structures like ListNode needed for this problem.

==Code Submission==

def deserialize_input(input_str: str):
    parts = input_str.strip().rsplit(' ', 1)
    coins_str = parts[0]
    k_str = parts[1]
    
    k = int(k_str)
    
    if not coins_str:
        coins = []
    else:
        coins = [int(c) for c in coins_str.split(',')]
    
    return coins, k

def serialize_output(result: int) -> str:
    return str(result)

if __name__ == '__main__':
    line = sys.stdin.read()
    
    coins_list, k_val = deserialize_input(line)
    
==Code Submission==
    sol = Solution()
    ans = sol.findKthSmallest(coins_list, k_val) # Python's int handles large numbers
    
    print(serialize_output(ans))