# Task 3: Python3 Test Case Runner (Fixed)
# No import statements here - will be auto-injected

# No helper classes needed before placeholder

==Code Submission==

# Function to parse the input string "values|edges"
def deserialize_stdin(input_str: str):
    try:
        stripped_input = input_str.strip()
        if not stripped_input:
             # Handle empty input after stripping
             # print("Error: Input is empty.", file=sys.stderr) # Debug
             return None, None
        # Ensure exactly one pipe separator exists
        parts = stripped_input.split('|', 1)
        if len(parts) != 2:
             # print("Error: Invalid input format, pipe separator issue.", file=sys.stderr) # Debug
             return None, None
        values_str, edges_str = parts
    except Exception as e: # Catch potential errors during initial split/strip
        # print(f"Error during initial input processing: {e}", file=sys.stderr) # Debug
        return None, None # Indicate failure

    try:
        # Parse values: list of integers
        # Filter out empty strings that might result from trailing commas etc.
        values = [int(v.strip()) for v in values_str.split(',') if v.strip()]
        if not values: # Constraint n>=2
             # print("Error: Values array is empty after parsing.", file=sys.stderr) # Debug
             return None, None
    except ValueError:
        # Handle error: Non-integer value found
        # print("Error: Non-integer found in values.", file=sys.stderr) # Debug
        return None, None
    except Exception as e: # Catch other potential errors during value parsing
        # print(f"Error parsing values: {e}", file=sys.stderr) # Debug
        return None, None

    edges = []
    n = len(values) # Get n based on parsed values

    # Only parse edges if edges_str is not empty and contains non-whitespace
    if edges_str and edges_str.strip():
        try:
            # Strip whitespace from the edges string before splitting
            edge_pairs = edges_str.strip().split(';')
            for pair in edge_pairs:
                # Filter out empty strings resulting from consecutive semicolons or trailing semicolon
                stripped_pair = pair.strip()
                if stripped_pair:
                    parts = stripped_pair.split(',')
                    if len(parts) != 2:
                         # print(f"Error: Malformed edge pair '{stripped_pair}'.", file=sys.stderr) # Debug
                         return None, None # Error on malformed pair
                    # Ensure parts are stripped before converting to int
                    u_str, v_str = parts[0].strip(), parts[1].strip()
                    # Check if parts are non-empty after stripping (handles cases like "1,")
                    if not u_str or not v_str:
                         # print(f"Error: Empty node index in edge pair '{stripped_pair}'.", file=sys.stderr) # Debug
                         return None, None
                    u, v = int(u_str), int(v_str)
                    # Basic validation for node indices (optional, depends on trust in generator)
                    # if not (0 <= u < n and 0 <= v < n):
                    #    print(f"Error: Node index out of bounds in edge [{u},{v}] for n={n}.", file=sys.stderr) # Debug
                    #    return None, None
                    edges.append([u, v])
        except ValueError:
            # Handle error: Non-integer edge index
            # print("Error: Non-integer found in edges.", file=sys.stderr) # Debug
            return None, None
        except Exception as e: # Catch other potential errors during edge parsing
            # print(f"Error parsing edges: {e}", file=sys.stderr) # Debug
            return None, None
    # If edges_str is empty or only whitespace, edges list remains empty.

    # Validate edge count: should be n-1 for n>=2
    # Relaxing this check based on previous attempts. Assuming the input generator
    # provides structurally valid trees even if the edge count serialization had issues.
    # If strict validation is needed, uncomment the check below.
    # if n >= 2 and len(edges) != n - 1:
    #      print(f"Warning: Edge count mismatch. n={n}, edges={len(edges)}. Expected {n-1} edges.", file=sys.stderr) # Debug
    #      # return None, None # Re-enable for strict validation

    # Handle n=1 case specifically if needed (though constraints say n>=2)
    # if n == 1 and len(edges) != 0:
    #    return None, None

    return edges, values

# Function to serialize the result (int) to string
def serialize_stdout(result) -> str:
    # Check if result is None or not an integer type (robustness)
    if result is None:
        # print("Error: Solution returned None.", file=sys.stderr) # Debug
        return "" # Return empty string if solution returns None
    try:
        # The problem asks for long long, Python's int handles arbitrary size
        return str(int(result)) # Ensure it's converted to int first, then string
    except (ValueError, TypeError):
        # print(f"Error: Cannot serialize non-integer result '{result}'.", file=sys.stderr) # Debug
        return "" # Return empty string for non-serializable types

# --- Main execution block ---

# Set a higher recursion depth suitable for the constraints (n <= 2 * 10^4)
try:
    required_limit = 2 * 10**4 + 500 # Based on n constraint + buffer
    current_limit = sys.getrecursionlimit()
    if required_limit > current_limit:
        # Cap the limit increase to avoid excessive memory or system limits
        safe_limit = min(required_limit, 30000) # Adjust cap if needed
        sys.setrecursionlimit(safe_limit)
except Exception as e:
    # print(f"Warning: Failed to set recursion limit - {e}", file=sys.stderr) # Debug
    pass # Continue with the existing limit if setting fails

# Read all input from stdin until EOF
input_data = sys.stdin.read()

# Proceed only if input_data is not empty after stripping whitespace
if input_data and input_data.strip():
    edges_list, values_list = deserialize_stdin(input_data)

    # Check if parsing was successful
    if edges_list is not None and values_list is not None:
        try:
            # Ensure Solution class is available (will be injected)
            sol = Solution()
            # Ensure the method name matches the starter code
            ans = sol.maximumScoreAfterOperations(edges_list, values_list)
            # Serialize and print the result
            output_str = serialize_stdout(ans)
            # Only print if serialization produced a non-empty string
            if output_str:
                 print(output_str)
            # else:
                 # Serialization failed or returned empty string
                 # print("Error: Serialization failed or produced empty output.", file=sys.stderr) # Debug
                 # pass # Do not print anything if serialization fails

        # Specific error handling (optional, but good for debugging)
        except RecursionError:
            # print("Runtime Error: Recursion depth exceeded.", file=sys.stderr) # Debug
            pass # Exit silently as required
        except NameError:
             # print("Error: Solution class or method not found.", file=sys.stderr) # Debug
             pass # Exit silently
        except Exception as e:
            # Handle other potential runtime errors in the solution code
            # print(f"Runtime Error: {type(e).__name__}: {e}", file=sys.stderr) # Debug
            pass # Exit silently as required
    # else:
        # Parsing error occurred, deserialize_stdin returned None
        # print("Error: Failed to parse input.", file=sys.stderr) # Debug
        pass # Exit silently

# else:
    # Handle case where stdin was empty or contained only whitespace
    # print("Error: Empty input received.", file=sys.stderr) # Debug
    pass # Exit silently