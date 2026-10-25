==Code Submission==

def deserialize_stdin(input_str):
    lines = input_str.strip().split("\n")
    s = lines[0].strip() if lines else ""
    queries = []
    if len(lines) > 1 and lines[1].strip() != "":
        for token in lines[1].split(";"):
            token = token.strip()
            if token:
                queries.append(list(map(int, token.split(","))))
    return s, queries

def serialize_stdout(result):
    return ",".join("true" if x else "false" for x in result)

data = sys.stdin.read()
s, queries = deserialize_stdin(data)
sol = Solution()
ans = sol.canMakePalindromeQueries(s, queries)
print(serialize_stdout(ans))