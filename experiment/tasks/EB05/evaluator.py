def evaluate(expected_output: str, program_output: str) -> bool:
    def deserialize_output(s):
        s = s.strip()
        if not s:
            return []
        return list(map(int, s.split(',')))
    try:
        expected = deserialize_output(expected_output)
        output = deserialize_output(program_output)
        return expected == output
    except Exception:
        return False