==Code Submission==

def deserialize_stdin(input_str):
    # Expect input as a comma-separated list of integers.
    if not input_str.strip():
        return []
    return list(map(int, input_str.strip().split(',')))

def serialize_stdout(result):
    return str(result)

data = sys.stdin.read().strip()
nums = deserialize_stdin(data)
sol = Solution()
ans = sol.sumDigitDifferences(nums)
print(serialize_stdout(ans))