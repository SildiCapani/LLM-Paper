class Solution {
    public long dfs(int i, List<Integer>[] adj, int[] v, int[] vis) {
        if (adj[i].size() == 1 && i != 0)
            return (long) v[i];
        long s = 0;
        vis[i] = 1;
        for (int j : adj[i]) {
            if (vis[j] == 1)
                continue;
            s += dfs(j, adj, v, vis);
        }
        return Math.min((long) v[i], s);
    }

    public long maximumScoreAfterOperations(int[][] edges, int[] values) {
        int n = values.length;
        List<Integer>[] adj = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            adj[i] = new ArrayList<>();
        }
        for (int i = 0; i < n - 1; i++) {
            adj[edges[i][0]].add(edges[i][1]);
            adj[edges[i][1]].add(edges[i][0]);
        }
        long s = 0;
        for (int i : values)
            s += i;
        int[] vis = new int[n];
        long k = dfs(0, adj, values, vis);
        return s - k;
    }
}