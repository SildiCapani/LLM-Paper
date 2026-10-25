def evaluate(expected_output: str, program_output: str) -> bool:
    # Deserialization logic: trim whitespace.
    expected = expected_output.strip()
    program = program_output.strip()
    try:
        # Attempt to compare numeric values.
        return int(expected) == int(program)
    except ValueError:
        # Fallback to string comparison if not integers.
        return expected == program