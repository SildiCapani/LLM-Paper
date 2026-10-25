==Code Submission==

vector<string> split(const string &s, char delim) {
    vector<string> elems;
    stringstream ss(s);
    string item;
    while(getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}

int main(){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string container_line, query_line;
    getline(cin, container_line);
    getline(cin, query_line);
    vector<string> wordsContainer = split(container_line, ',');
    vector<string> wordsQuery = split(query_line, ',');
    Solution sol;
    vector<int> ans = sol.stringIndices(wordsContainer, wordsQuery);
    string output;
    for (size_t i = 0; i < ans.size(); i++){
        output += to_string(ans[i]);
        if(i < ans.size() - 1)
            output += ",";
    }
    cout << output;
    return 0;
}