==Code Submission==

def deserialize_stdin(input_str):
    arr_str, s = input_str.strip().split(' ', 1)
    parent = list(map(int, arr_str.split(','))) if arr_str else []
    return parent, s

def serialize_stdout(result):
    return ",".join(map(str, result))

data = sys.stdin.read().strip()
parent, s = deserialize_stdin(data)
sol = Solution()  # The submitted solution will replace this placeholder.
ans = sol.findSubtreeSizes(parent, s)
sys.stdout.write(serialize_stdout(ans))