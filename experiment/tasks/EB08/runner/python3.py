==Code Submission==

def deserialize_stdin(input_str):
    # Our serialization format: "start,finish,limit,s"
    parts = input_str.strip().split(',')
    start = int(parts[0])
    finish = int(parts[1])
    limit = int(parts[2])
    s = parts[3]
    return start, finish, limit, s

def serialize_stdout(result):
    return str(result)

data = sys.stdin.read().strip()
start, finish, limit, s = deserialize_stdin(data)
sol = Solution()
ans = sol.numberOfPowerfulInt(start, finish, limit, s)
print(serialize_stdout(ans))