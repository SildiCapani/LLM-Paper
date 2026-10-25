==Code Submission==

pair<vector<int>, string> deserialize_stdin(const string &input) {
    size_t pos = input.find(' ');
    string parentStr = input.substr(0, pos);
    string s = input.substr(pos + 1);
    vector<int> parent;
    string token;
    stringstream ss(parentStr);
    while(getline(ss, token, ',')) {
        parent.push_back(stoi(token));
    }
    return {parent, s};
}

string serialize_stdout(const vector<int>& result) {
    string out;
    for (size_t i = 0; i < result.size(); i++) {
        if (i > 0) out += ",";
        out += to_string(result[i]);
    }
    return out;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string line;
    getline(cin, line);
    auto pr = deserialize_stdin(line);
    vector<int> parent = pr.first;
    string s = pr.second;
    Solution sol; // The submitted solution will replace the placeholder code.
    vector<int> ans = sol.findSubtreeSizes(parent, s);
    cout << serialize_stdout(ans) << "\n";
    return 0;
}