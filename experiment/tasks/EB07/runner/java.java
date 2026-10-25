// Task 3: Java Test Case Runner
// No import statements here - will be auto-injected

// The Main class should be the first class in the file for Java execution
public class Main {

    // Helper class to hold deserialized input
    private static class InputData {
        int[][] edges;
        int[] values;
        boolean parseError = false; // Flag to indicate parsing issues

        InputData(int[][] edges, int[] values) {
            this.edges = edges;
            this.values = values;
        }
        InputData() { // Constructor for error case
             this.parseError = true;
        }
    }

    // Function to parse the input string "values|edges"
    private static InputData deserialize_stdin(String input) {
        String[] parts = input.split("\\|", 2);
        if (parts.length != 2) {
            System.err.println("Input format error: Pipe separator missing or invalid.");
            return new InputData(); // Return error state
        }
        String values_str = parts[0];
        String edges_str = parts[1];

        int[] values;
        try {
             if (values_str.isEmpty()) {
                 values = new int[0];
             } else {
                 values = Arrays.stream(values_str.split(","))
                                .filter(s -> !s.isEmpty())
                                .mapToInt(Integer::parseInt)
                                .toArray();
             }
             if (values.length == 0) { // Constraint n>=2
                  System.err.println("Input error: Values array is empty.");
                  return new InputData();
             }
        } catch (NumberFormatException e) {
             System.err.println("Error parsing values: " + e.getMessage());
             return new InputData();
        }

        int[][] edges;
        try {
            if (edges_str.isEmpty()) {
                 // If n=2, edges_str might be "0,1". If truly empty, it's an error for n>=2.
                 if (values.length == 2) { // Special case n=2, expect one edge
                      System.err.println("Input error: Edges string empty for n=2.");
                      // Allow proceeding if generator guarantees format, otherwise return error
                      // Let's assume format is correct and proceed if n=2, expecting edge later? No, parse what's given.
                      edges = new int[0][2]; // Treat as error or incomplete input
                      // return new InputData(); // More strict error handling
                 } else if (values.length > 2) {
                      System.err.println("Input error: Edges string empty for n > 2.");
                      return new InputData();
                 } else { // n < 2, should not happen based on constraints
                      edges = new int[0][2];
                 }

            } else {
                String[] edge_pairs = edges_str.split(";");
                List<String> valid_edge_pairs = Arrays.stream(edge_pairs)
                                                      .filter(s -> !s.isEmpty() && s.contains(","))
                                                      .collect(Collectors.toList());

                // Validate edge count: should be n-1
                if (valid_edge_pairs.size() != values.length - 1) {
                     System.err.println("Input error: Incorrect number of edges. Expected " + (values.length - 1) + ", found " + valid_edge_pairs.size());
                     // return new InputData(); // Strict validation
                }

                edges = new int[valid_edge_pairs.size()][2];
                for (int i = 0; i < valid_edge_pairs.size(); i++) {
                    String pair = valid_edge_pairs.get(i);
                    String[] uv = pair.split(",", 2);
                    if (uv.length == 2) {
                         edges[i][0] = Integer.parseInt(uv[0]);
                         edges[i][1] = Integer.parseInt(uv[1]);
                    } else {
                         System.err.println("Malformed edge pair: " + pair);
                         return new InputData(); // Error on malformed edge
                    }
                }
            }
        } catch (NumberFormatException e) {
             System.err.println("Error parsing edges: " + e.getMessage());
             return new InputData();
        }

        return new InputData(edges, values);
    }

    // Function to serialize the result (long) to string
    private static String serialize_stdout(long result) {
        return String.valueOf(result);
    }

    // Main execution method
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();

        if (line == null || line.trim().isEmpty()) {
             System.err.println("Input is empty.");
             return; // Exit if input is empty
        }
        line = line.trim();

        InputData inputData = deserialize_stdin(line);

        // Check if parsing failed
        if (inputData.parseError || inputData.values == null || inputData.edges == null) {
             System.err.println("Failed to parse input or input invalid.");
             return; // Exit if parsing failed
        }

        Solution sol = new Solution();
        long ans = sol.maximumScoreAfterOperations(inputData.edges, inputData.values);

        System.out.println(serialize_stdout(ans));
    }
}

// The placeholder for the Solution class goes AFTER the Main class
==Code Submission==