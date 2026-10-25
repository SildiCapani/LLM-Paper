def evaluate(expected_output: str, program_output: str) -> bool:
    def deserialize_output(s):
        s = s.strip()
        if s == "":
            return []
        return list(map(int, s.split(',')))
    exp = deserialize_output(expected_output)
    prog = deserialize_output(program_output)
    return exp == prog