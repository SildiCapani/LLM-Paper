int a[50001][26], b[50001][26];
class Solution {
public:
    bool checkAvailable(int x1, int y1, int x2, int y2, bool flag){
        for(int i = 0; i < 26; i++){
            if(flag && a[y1][i] - a[x1-1][i] < b[y2][i] - b[x2-1][i])
                return false;
            if(!flag && a[y1][i] - a[x1-1][i] > b[y2][i] - b[x2-1][i])
                return false;
        }
        return true;
    }

    bool checkRest(int &x1, int &y1, int &x2, int &y2, set<int> &st){
        int mx = max(y1, y2), mn = min(x1, x2);

        auto it = st.lower_bound(0);
        if(it != st.end() && *it < mn) return false;
        it = st.upper_bound(mx);
        if(it != st.end()) return false;

        if(y1 < x2){
            it = st.upper_bound(y1);
            if(it != st.end() && *it < x2) return false;
        }
        if(y2 < x1){
            it = st.upper_bound(y2);
            if(it != st.end() && *it < x1) return false;
        }
        return true;
    }

    vector<bool> canMakePalindromeQueries(string s, vector<vector<int>>& queries) {
        int n = s.size();
        vector<bool> ans;
        set<int> st;
        
        for(int i = 0; i < n; i++){
            if(i < n/2){
                for(int j = 0; j < 26; j++) a[i+1][j] = a[i][j];
                a[i+1][s[i]-'a']++;
            }
            else{
                for(int j = 0; j < 26; j++) b[i+1-n/2][j] = b[i-n/2][j];
                b[i+1-n/2][s[n-1-(i-n/2)]-'a']++;
            }

            if(i < n/2 && s[i] != s[n-1-i]) st.insert(i+1);
        }   

        for(int i = 0; i < 26; i++)
            if(a[n/2][i] != b[n/2][i])
                return vector<bool>(queries.size(), false);

        for(auto &i : queries){
            bool val = true;
            int &x1 = i[0], &y1 = i[1], &x2 = i[3], &y2 = i[2];
            x1++, y1++, y2 = n-y2, x2 = n-x2;

            if(!checkRest(x1, y1, x2, y2, st)) val = false;

            if(x1 < x2 && !checkAvailable(x1, y1, x1, min(x2-1, y1), true))
                val = false;
            if(x2 < x1 && !checkAvailable(x2, min(x1-1, y2), x2, y2, false))
                val = false;
            if(y1 < y2 && !checkAvailable(max(y1+1, x2), y2, x2, y2, false))
                val = false;
            if(y2 < y1 && !checkAvailable(x1, y1, max(y2+1, x1), y1, true))
                val = false;
            
            ans.push_back(val);
        }
        return ans;
    }
};