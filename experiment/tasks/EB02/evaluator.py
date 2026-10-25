def evaluate(expected_output: str, program_output: str) -> bool:
    # Helper to deserialize output strings
    def deserialize(s: str) -> int:
        # Program output might have trailing whitespace/newlines
        return int(s.strip())

    try:
        expected_val = deserialize(expected_output)
        program_val = deserialize(program_output)
        return expected_val == program_val
    except ValueError:
        # If parsing fails, it's not a match
        return False
    except Exception:
        # Other unexpected errors
        return False