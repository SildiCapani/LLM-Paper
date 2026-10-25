def evaluate(expected_output: str, program_output: str) -> bool:
    # Deserialization: here our outputs are simple integers serialized as strings.
    try:
        expected = int(expected_output.strip())
        program_val = int(program_output.strip())
        return expected == program_val
    except Exception:
        return False