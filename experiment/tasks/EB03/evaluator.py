def evaluate(expected_output: str, program_output: str) -> bool:
    # Deserialization: Our output format is a simple integer string.
    try:
        expected = int(expected_output.strip())
        actual = int(program_output.strip())
    except Exception:
        return False
    return expected == actual