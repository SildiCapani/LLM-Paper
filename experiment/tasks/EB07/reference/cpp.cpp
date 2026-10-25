class Solution {
public:

    //subtree => {所有path至少都有一個點不存在,所有點都存在}
    pair<long long,long long> Dynamicprogramming(vector<vector<int>>& adj, vector<unsigned char>& visited, vector<int>& values, int index) {
        visited[index] = 1;

        bool hasChild = false;
        long long atleast1 = 0, total = 0;
        pair<long long,long long> result;
        for(int child : adj[index]) {
            if(visited[child] == 0) {
                result = Dynamicprogramming(adj, visited, values, child);
                atleast1 += result.first;
                total += result.second;
                hasChild = true;
            }
        }

        //base case:
        if(hasChild == false) {
            //cout << "base => index: " << index << endl;
            return {0, values[index]};
        }  

        //cout << "index: " << index << " atleast1: " << atleast1 << " total: " << total << endl; 
        if(index != 0)
            return {max(total, values[index] + atleast1), values[index] + total};
        else
            return {total, values[index] + atleast1};
    }

    //這題題意上不是很好理解,簡單來說就是可以在tree上取走一些節點.
    //但有個前提就是拿走的這些節點,不能造成Path的sum變為0.
    //然後在這個前提之下,想辦法拿到最多加總值的節點
    //所以很明顯得用DP去解,且滿足兩個條件.
    //1.節點可決定取或不取
    //2.想辦法找出max value
    //subtree => {所有path至少都有一個點不存在,所有點都存在}
    //root => max((root->val + 至少一個點不存在), 所有點都存在);
    long long maximumScoreAfterOperations(vector<vector<int>>& edges, vector<int>& values) {
        ios_base::sync_with_stdio(0);
        cin.tie(NULL);
        cout.tie(NULL);

        int limit = values.size(), edges_limit = edges.size();
        //1.先create雙向相鄰串列和visted array;
        vector<vector<int>> adj(limit);
        vector<unsigned char> visited(limit);
        for(int i = 0; i < edges_limit; ++i) {
            int u = edges[i][0], v = edges[i][1];
            adj[u].push_back(v);
            adj[v].push_back(u);
        }

        //2.create Dynamic programming的DFS for all path and return answer
        //  max((root->val + 所有路徑至少有一點不存在)),所有點都存在)
        pair<long long,long long> result = Dynamicprogramming(adj, visited, values, 0);
        return max(result.first, result.second);
    }
};