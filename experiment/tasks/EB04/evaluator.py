def evaluate(expected_output: str, program_output: str) -> bool:
    """
    Compares the serialized expected output with the serialized program output.
    Outputs are single integers.
    """
    try:
        # Trim whitespace (including newlines) from program_output
        # Expected output from generator should already be clean.
        expected_val = int(expected_output.strip())
        program_val = int(program_output.strip())
        
        return expected_val == program_val
    except ValueError:
        # If either output cannot be converted to an integer,
        # it's a format error, hence not a match.
        return False
    except Exception:
        # Catch any other potential errors during processing.
        return False