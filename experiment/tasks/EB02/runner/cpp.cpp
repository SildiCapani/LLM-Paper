==Code Submission==

std::pair<std::vector<int>, int> deserialize_stdin(const std::string& input_str) {
    std::vector<int> coins;
    int k_val;

    std::string s = input_str; 
    
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch){ return !std::isspace(ch); }));
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch){ return !std::isspace(ch); }).base(), s.end());

    std::string coins_part_str;
    std::string k_part_str;

    size_t last_space_pos = s.rfind(' ');
    
    if (last_space_pos == std::string::npos) {
        coins_part_str = "";
        k_part_str = s;
    } else {
        coins_part_str = s.substr(0, last_space_pos);
        k_part_str = s.substr(last_space_pos + 1);
    }

    k_val = std::stoi(k_part_str);

    if (!coins_part_str.empty()) {
        std::stringstream ss_coins(coins_part_str);
        std::string segment;
        while(std::getline(ss_coins, segment, ',')) {
            if (!segment.empty()) {
                 std::string temp_segment = segment;
                 temp_segment.erase(temp_segment.begin(), std::find_if(temp_segment.begin(), temp_segment.end(), [](unsigned char ch){ return !std::isspace(ch); }));
                 temp_segment.erase(std::find_if(temp_segment.rbegin(), temp_segment.rend(), [](unsigned char ch){ return !std::isspace(ch); }).base(), temp_segment.end());
                 if(!temp_segment.empty()){ 
                    coins.push_back(std::stoi(temp_segment));
                 }
            }
        }
    }
    
    return std::make_pair(coins, k_val);
}

std::string serialize_stdout(long long result) {
    return std::to_string(result);
}

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string input_line;
    std::getline(std::cin, input_line);
    
    std::pair<std::vector<int>, int> parsed_input = deserialize_stdin(input_line);
    std::vector<int> parsed_coins = parsed_input.first;
    int parsed_k = parsed_input.second;

    Solution sol;
    long long ans = sol.findKthSmallest(parsed_coins, parsed_k);

    std::cout << serialize_stdout(ans) << std::endl;

    return 0;
}