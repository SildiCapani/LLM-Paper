==Code Submission==

def deserialize_stdin(input_str):
    lines = input_str.strip().splitlines()
    wordsContainer = lines[0].split(',') if lines else []
    wordsQuery = lines[1].split(',') if len(lines) > 1 else []
    return wordsContainer, wordsQuery

def serialize_stdout(result):
    return ",".join(str(x) for x in result)

if __name__ == '__main__':
    input_str = sys.stdin.read()
    wordsContainer, wordsQuery = deserialize_stdin(input_str)
    sol = Solution()
    ans = sol.stringIndices(wordsContainer, wordsQuery)
    print(serialize_stdout(ans))