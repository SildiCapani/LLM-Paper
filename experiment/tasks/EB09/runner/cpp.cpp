==Code Submission==

vector<int> deserialize_stdin(const string& input) {
    vector<int> prices;
    stringstream ss(input);
    string token;
    while(getline(ss, token, ',')) {
        if(!token.empty())
            prices.push_back(stoi(token));
    }
    return prices;
}

string serialize_stdout(int result) {
    return to_string(result);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string line;
    getline(cin, line);
    vector<int> prices = deserialize_stdin(line);
    Solution sol;  // The submitted solution will be injected into the Solution class.
    int ans = sol.minimumCoins(prices);
    cout << serialize_stdout(ans);
    return 0;
}