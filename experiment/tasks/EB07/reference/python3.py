class Solution:
    def maximumScoreAfterOperations(self, edges: List[List[int]], values: List[int]) -> int:
        n = len(edges)+1
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        def dfs(i, p):
            # returns result_if_healthy_ancestor, result_if_no_healthy_ancestor
            if len(adj[i]) == 1 and i != 0:
                # if leaf node, exit early
                return values[i], 0
            if_healthy_ancestor = 0
            if_no_healthy_ancestor = 0
            for j in adj[i]:
                if j == p:
                    continue
                sub_healthy, sub_no_healthy = dfs(j, i)
                if_healthy_ancestor += sub_healthy
                if_no_healthy_ancestor += sub_no_healthy
            return values[i]+if_healthy_ancestor, max(if_healthy_ancestor, values[i]+if_no_healthy_ancestor)
        
        return dfs(0, -1)[1]