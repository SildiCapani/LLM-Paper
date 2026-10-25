==Code Submission==

vector<vector<int>> deserializeQueries(const string &qLine) {
    vector<vector<int>> queries;
    if(qLine.empty()) return queries;
    size_t start = 0, pos;
    while((pos = qLine.find(';', start)) != string::npos){
        string token = qLine.substr(start, pos - start);
        if(!token.empty()){
            vector<int> query;
            stringstream ss(token);
            string num;
            while(getline(ss, num, ',')){
                query.push_back(stoi(num));
            }
            if(query.size() == 4)
                queries.push_back(query);
        }
        start = pos + 1;
    }
    string token = qLine.substr(start);
    if(!token.empty()){
        vector<int> query;
        stringstream ss(token);
        string num;
        while(getline(ss, num, ',')){
            query.push_back(stoi(num));
        }
        if(query.size() == 4)
            queries.push_back(query);
    }
    return queries;
}

string serializeOutput(const vector<bool>& result) {
    string out;
    for (size_t i = 0; i < result.size(); i++){
        out += (result[i] ? "true" : "false");
        if(i != result.size() - 1)
            out += ",";
    }
    return out;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s;
    getline(cin, s);
    string queriesLine;
    getline(cin, queriesLine);
    vector<vector<int>> queries = deserializeQueries(queriesLine);
    Solution sol;
    vector<bool> ans = sol.canMakePalindromeQueries(s, queries);
    cout << serializeOutput(ans);
    return 0;
}