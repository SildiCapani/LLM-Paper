==Code Submission==

def deserialize_stdin(input_str):
    # Expecting comma-separated integers.
    if not input_str:
        return []
    return list(map(int, input_str.strip().split(',')))

def serialize_stdout(result):
    return str(result)

line = sys.stdin.read().strip()
power = deserialize_stdin(line)
sol = Solution()
ans = sol.maximumTotalDamage(power)
print(serialize_stdout(ans))