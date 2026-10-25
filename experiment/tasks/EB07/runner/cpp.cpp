// Task 3: C++ Test Case Runner
// No #include or using namespace std; - will be auto-injected

// No helper classes needed before placeholder

==Code Submission==

// Function to parse the input string "values|edges"
std::pair<std::vector<std::vector<int>>, std::vector<int>> deserialize_stdin(const std::string& input) {
    size_t pipe_pos = input.find('|');
    if (pipe_pos == std::string::npos) {
         // Return empty vectors to indicate error, main function should check
         return {{}, {}};
    }
    std::string values_str = input.substr(0, pipe_pos);
    std::string edges_str = input.substr(pipe_pos + 1);

    std::vector<int> values;
    std::stringstream ss_values(values_str);
    std::string value_token;
    while (std::getline(ss_values, value_token, ',')) {
        if (!value_token.empty()) {
             try {
                values.push_back(std::stoi(value_token));
             } catch (const std::exception& e) { // Catch potential stoi errors
                 // Handle or ignore parsing errors for values
                 // For robustness, could return error indicator
                 return {{}, {}}; // Indicate error
             }
        }
    }

    std::vector<std::vector<int>> edges;
    std::stringstream ss_edges(edges_str);
    std::string edge_token;
    if (!edges_str.empty()) {
        while (std::getline(ss_edges, edge_token, ';')) {
            if (!edge_token.empty()) {
                size_t comma_pos = edge_token.find(',');
                if (comma_pos != std::string::npos) {
                     try {
                        int u = std::stoi(edge_token.substr(0, comma_pos));
                        int v = std::stoi(edge_token.substr(comma_pos + 1));
                        edges.push_back({u, v});
                     } catch (const std::exception& e) { // Catch potential stoi errors
                         // Handle or ignore parsing errors for edges
                         return {{}, {}}; // Indicate error
                     }
                } else {
                     // Malformed edge pair (no comma)
                     return {{}, {}}; // Indicate error
                }
            }
        }
    }
    
    // Basic validation: n>=2 means values should not be empty
    if (values.empty()) {
        return {{}, {}}; // Indicate error
    }
    // n = values.size(), edges should have n-1 elements
    if (edges.size() != values.size() - 1 && values.size() >= 2) {
         // This check might be too strict if input format allows variations
         // but based on problem constraints, it should hold.
         // return {{}, {}}; // Indicate error
    }

    return {edges, values};
}

// Function to serialize the result (long long) to string
std::string serialize_stdout(long long result) {
    return std::to_string(result);
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(NULL);

    std::string line;
    if (!std::getline(std::cin, line)) {
        return 1; // Error reading input
    }

    auto [edges, values] = deserialize_stdin(line);

    // Check if deserialization failed (indicated by empty values vector)
    if (values.empty()) {
         // Optionally print error to stderr
         // std::cerr << "Failed to parse input." << std::endl;
         return 1; // Indicate error
    }

    Solution sol;
    long long ans = sol.maximumScoreAfterOperations(edges, values);

    std::cout << serialize_stdout(ans) << std::endl;

    return 0;
}