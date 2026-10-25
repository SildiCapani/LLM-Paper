// No other imports are needed; they are auto-injected.
// No package declaration.

public class Main {

    /**
     * Deserializes a comma-separated string into an integer array.
     * Handles trimming of whitespace and empty input.
     *
     * @param input The comma-separated string.
     * @return The deserialized integer array.
     */
    private static int[] deserializeIntArray(String input) {
        // Trim whitespace from the input string
        input = input.trim();
        // Handle empty input string case
        if (input.isEmpty()) {
            return new int[0];
        }
        // Split the string by comma, trim each part, filter out empty strings,
        // and parse to integers.
        try {
            return Arrays.stream(input.split(","))
                         .map(String::trim)
                         .filter(s -> !s.isEmpty()) // Ensure robustness against empty parts like "1,,2"
                         .mapToInt(Integer::parseInt)
                         .toArray();
        } catch (NumberFormatException e) {
            // Handle potential parsing errors if input is malformed
            System.err.println("Error parsing input string: " + input);
            // Depending on requirements, might throw exception or return default/empty array
            return new int[0]; // Or throw new IllegalArgumentException("Invalid input format");
        }
    }

    /**
     * Serializes an integer result into a string.
     *
     * @param result The integer result.
     * @return The string representation of the integer.
     */
    private static String serializeInt(int result) {
        return String.valueOf(result);
    }

    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
        
        // Read the single line of input containing the comma-separated integers
        String line = reader.readLine();
        
        // Handle null line case (e.g., empty input stream)
        if (line == null) {
            line = ""; // Treat as empty input
        }

        // Deserialize the input string into an int array
        int[] prices = deserializeIntArray(line);

        // Instantiate the Solution class (the actual implementation will be injected)
        Solution sol = new Solution();

        // Call the solution method
        int ans = sol.minimumCoins(prices);

        // Serialize the integer result to a string
        String output = serializeInt(ans);

        // Print the result to standard output without a trailing newline
        System.out.print(output);
        
        reader.close(); // Close the reader
    }
}

// The Solution class implementation will be injected below this line
==Code Submission==

// Any necessary helper classes (like ListNode, TreeNode, etc.) would go here,
// but this problem doesn't seem to require them.
// The Solution class itself will be injected replacing the placeholder line above.