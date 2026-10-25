class Solution {
    vector<long> _processOut(vector<int>& coins) {
        ranges::sort(coins);
        int n = coins.size();
        if (coins[0] == 1) return {1};
        vector<long> longCoins;
        for (int coin: coins) {
            for (int lcoin: longCoins) {
                if (coin % lcoin == 0) goto next;
            }
            longCoins.push_back(coin);
            next:;
        }
        return longCoins;
    }
    bool _next(vector<int>& indexes, int n) {
        int i = n - 1;
        while (i >= 0 && indexes[i] == indexes[i + 1] - 1) --i;
        if (i < 0) return false;
        indexes[i]++;
        for (++i; i < n; ++i) indexes[i] = indexes[i - 1] + 1;
        return true;
    }
    void _appendWithCombinations(vector<long>& coins, long upper) {
        int sign{-1};
        const int n = coins.size();
        vector<int> indexes(n + 1);
        for (int i{2}; i <= n; ++i, sign = -sign) {
            for (int j{}; j < i; ++j) indexes[j] = j;
            indexes[i] = n;
            do {
                long prod = 1;
                for (int j{}; j < i; ++j) prod = lcm(prod, coins[indexes[j]]);
                if (prod <= upper) coins.push_back(sign*prod);
            } while (_next(indexes, i));
        }
    }
public:
    long findKthSmallest(vector<int>& poorCoins, int k) {
        ios::sync_with_stdio(false);cin.tie(NULL);cout.tie(NULL);
        vector<long> coins = _processOut(poorCoins);
        const int n = coins.size();
        if (n == 1) return k*coins[0];
        double divider{};
        for (auto coin: coins) divider += 1./coin;
        long upper{coins[0]*k + 1};
        long lower = k/divider;
        _appendWithCombinations(coins, upper);
        while (lower < upper) {
            long mid = (lower + upper)/2;
            long term{};
            long minReminder{numeric_limits<long>::max()};
            for (long coin: coins) {
                auto [q, r] = div(mid, coin);
                term += q;
                minReminder = min(minReminder, r);
            }
            if (term == k) return mid - minReminder;
            if (term < k) lower = mid;
            else upper = mid - minReminder;
            while (upper < abs(coins.back())) coins.pop_back();
        }
        return -1;
    }
};