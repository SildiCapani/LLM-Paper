class Solution:
    def minimumCoins(self, prices: List[int]) -> int:
        prices = [0] + prices
        n = len(prices)
        if n <= 3:
            return prices[1]
        dp = [0] * n
        dp[1] = dp[2] = prices[1]
        q = deque([2])

        for i in range(3, n):
            while q and q[0] * 2 < i:
                q.popleft()

            dp[i] = dp[i - 1] + prices[i]
            if q:
                dp[i] = min(dp[i], dp[q[0] - 1] + prices[q[0]])

            while q and dp[q[-1] - 1] + prices[q[-1]] >= dp[i - 1] + prices[i]:
                q.pop()
            q.append(i)

        return dp[-1]