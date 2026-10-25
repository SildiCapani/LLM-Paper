class Solution:
    def findKthSmallest(self, coins: List[int], k: int) -> int:
        coins.sort()
        coins_mutex = []
        for coin in coins:
            for candidate in coins_mutex:
                if coin % candidate == 0:
                    break
            else:
                coins_mutex.append(coin)

        if len(coins_mutex) == 1:
            return coins_mutex[0] * k

        lcms: Dict[int, int] = defaultdict(int)
        self.find_lcm(0, 1, 1, coins_mutex, lcms)

        left, right = k, coins_mutex[0] * k
        while left <= right:
            middle = left + (right - left) // 2
            amount = 0
            for denomination in lcms.keys():
                amount += middle // denomination * lcms[denomination]

            if amount >= k:
                right = middle - 1
            else:
                left = middle + 1
        return left

    def find_lcm(self, index: int, base: int, add_or_remove: int, coins: List[int], lcms: Dict[int, int]):
        for index_next in range(index, len(coins)):
            lcm = math.lcm(base, coins[index_next])
            lcms[lcm] += add_or_remove
            if lcms[lcm] == 0:
                del lcms[lcm]

            self.find_lcm(index_next+1, lcm, -add_or_remove, coins, lcms)