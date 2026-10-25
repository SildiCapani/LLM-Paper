class Solution:
    def maximumTotalDamage(self, power: List[int]) -> int:
        power = Counter(power)
        n = len(power)
        dp = [0]*(n+1)
        keys = sorted([i for i in power.keys()])
        dp[1] = power[keys[0]]*keys[0]
        if n==1:
            return dp[1]
        
        if keys[1]-keys[0]>2:
            dp[2] = dp[1] + power[keys[1]]*keys[1]
        else:
            dp[2] = max(power[keys[1]]*keys[1], power[keys[0]]*keys[0])

        for i in range(2, n):
            if keys[i]-keys[i-1]>2:
                dp[i+1] = dp[i] + power[keys[i]]*keys[i]
            elif keys[i]-keys[i-2]>2:
                dp[i+1] = max(dp[i], dp[i-1] + power[keys[i]]*keys[i])
            else:
                dp[i+1] = max(dp[i], dp[i-2] + power[keys[i]]*keys[i])
        return dp[-1]