==Code Submission==

def deserialize_stdin(input_str):
    input_str = input_str.strip()
    if not input_str:
        return []
    return list(map(int, input_str.split(',')))

def serialize_stdout(result):
    return str(result)

input_str = sys.stdin.read().strip()
prices = deserialize_stdin(input_str)
sol = Solution()  # The submitted solution will be injected here.
ans = sol.minimumCoins(prices)
sys.stdout.write(serialize_stdout(ans))