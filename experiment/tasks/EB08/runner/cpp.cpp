==Code Submission==

pair<long long, pair<long long, pair<int, string>>> deserialize_stdin(const string &input) {
    // Our serialization format: "start,finish,limit,s"
    stringstream ss(input);
    string token;
    getline(ss, token, ',');
    long long start = stoll(token);
    getline(ss, token, ',');
    long long finish = stoll(token);
    getline(ss, token, ',');
    int limit = stoi(token);
    string s;
    getline(ss, s);
    return {start, {finish, {limit, s}}};
}

string serialize_stdout(long long result) {
    return to_string(result);
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string line;
    getline(cin, line);
    auto data = deserialize_stdin(line);
    long long start = data.first;
    long long finish = data.second.first;
    int limit = data.second.second.first;
    string s = data.second.second.second;
    
    Solution sol;
    long long ans = sol.numberOfPowerfulInt(start, finish, limit, s);
    cout << serialize_stdout(ans);
    return 0;
}