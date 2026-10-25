def evaluate(expected_output: str, program_output: str) -> bool:
    # Our serialization format outputs a single integer as a string.
    try:
        expected = int(expected_output.strip())
        output = int(program_output.strip())
        return expected == output
    except Exception:
        return expected_output.strip() == program_output.strip()