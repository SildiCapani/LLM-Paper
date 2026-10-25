# Task 2: Test Case Evaluator (Python)
def evaluate(expected_output: str, program_output: str) -> bool:
    # Helper function for deserialization (consistent with Task 1)
    def deserialize_output(output_str: str) -> int | None:
        try:
            cleaned_output = output_str.strip()
            if not cleaned_output:
                 return None
            # Use int() which handles large integers in Python
            return int(cleaned_output)
        except ValueError: # Handles non-integer strings
            return None
        except Exception: # Handles other potential errors
            return None

    expected_val = deserialize_output(expected_output)
    program_val = deserialize_output(program_output)

    # Check if deserialization was successful for both
    if expected_val is None:
        # This indicates an issue with the test case generator or format
        # Log or handle this error, but for evaluation, consider it a mismatch
        # print(f"Evaluator Error: Could not parse expected_output: {expected_output}")
        return False
    if program_val is None:
        # Program output was invalid (empty, non-integer, etc.)
        return False

    # Compare the integer values
    return expected_val == program_val