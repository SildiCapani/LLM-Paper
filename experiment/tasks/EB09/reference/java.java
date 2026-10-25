public class Solution {
    int[][] dp = new int[1001][1001];

    public int solve(int s, int[] v, int pow) {
        int n = v.length;
        if (s >= n)
            return 0;
        if (dp[s][pow] != -1)
            return dp[s][pow];
        if (pow == 0) {
            return v[s] + solve(s + 1, v, s + 1);
        }
        int ans = solve(s + pow, v, 0);
        for (int i = s; i <= Math.min(n - 1, s + pow - 1); i++) {
            ans = Math.min(ans, v[i] + solve(i + 1, v, i + 1));
        }
        return dp[s][pow] = ans;
    }

    public int minimumCoins(int[] v) {
        int n = v.length;
        for (int[] row : dp) {
            Arrays.fill(row, -1);
        }
        int ans = solve(0, v, 0);
        return ans;
    }
}