==Code Submission==

vector<int> deserialize_stdin(const string &input) {
    vector<int> result;
    string token;
    for (char ch : input) {
        if (ch == ',') {
            if (!token.empty()) {
                result.push_back(stoi(token));
                token.clear();
            }
        } else {
            token.push_back(ch);
        }
    }
    if (!token.empty()) {
        result.push_back(stoi(token));
    }
    return result;
}

string serialize_stdout(long long result) {
    return to_string(result);
}

int main(){
    string line;
    getline(cin, line);
    vector<int> power = deserialize_stdin(line);
    Solution sol;
    long long ans = sol.maximumTotalDamage(power);
    cout << serialize_stdout(ans);
    return 0;
}