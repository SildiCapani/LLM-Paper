def evaluate(expected_output: str, program_output: str) -> bool:
    def deserialize_output(s: str) -> list:
        s = s.strip()
        if not s:
            return []
        return [True if token.strip().lower() == "true" else False for token in s.split(",")]
    
    expected_vals = deserialize_output(expected_output)
    program_vals = deserialize_output(program_output)
    return expected_vals == program_vals