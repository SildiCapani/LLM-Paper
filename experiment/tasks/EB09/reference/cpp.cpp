/*
26 18 6 12 49 7 45 45
0   1 2  3  4 5 6  7 
i = 2; j = 3 -> 2+2+1 = 2*i+1
i = 3; j = 4 -> <= 2*i+1 = 7
*/

class Solution {
public:
    int minimumCoins(vector<int>& prices) 
    {
        ios::sync_with_stdio(false); cin.tie(0);
        int n = prices.size();
        vector<int> dp(n+1, INT_MAX);
        dp[n-1] = prices[n-1];
        for (int i = n-2; i >= 0; i --)
        {
            for (int j = i+1; j <= min(n, 2*i+2); j++)
            {
                if (j == n) dp[i] = prices[i];
                else dp[i] = min(dp[i], prices[i] + dp[j]);
            }
        }
        return dp[0];
    }
};