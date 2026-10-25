==Code Submission==

vector<int> deserialize_stdin(const string &input) {
    vector<int> nums;
    string token;
    istringstream ss(input);
    while(getline(ss, token, ',')) {
        if(!token.empty()) {
            nums.push_back(stoi(token));
        }
    }
    return nums;
}

string serialize_stdout(long long result) {
    return to_string(result);
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string line;
    getline(cin, line);
    vector<int> nums = deserialize_stdin(line);
    Solution sol;
    long long ans = sol.sumDigitDifferences(nums);
    cout << serialize_stdout(ans);
    return 0;
}