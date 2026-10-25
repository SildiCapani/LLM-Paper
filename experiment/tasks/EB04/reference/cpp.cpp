constexpr int m = 100000;
long long fact[m+1], inv_fact[m+1], mod = 1000000007;
bool init = false;
class Solution {
    // Time complexity O(slogm); Memory complexity O(m);
public:
    int numberOfSequence(int n, vector<int>& sick) {
        // (sum(segments))!/(multiply(for each segments!)) * 2 ^ (sum(segments)-len(segments));
        if (!init) {
            init = fact[0] = 1;
            // we only need modular factorials and inverse factorials up to mx inclusive:
            for (int i=1;i<=m;i++) 
                fact[i] = i * fact[i-1] % mod;
            // FLT: a^(p-1)%p = 1
            // a * a^(p-2)%p = a^-1
            // thus:
            // a * a^(p-2) = a^(p-1) * a^-1 = 1 * a^(-1) (mod p)
            // a^-1 = a^(p-2)
            inv_fact[m] = modPow(fact[m], mod - 2, mod);
            for (int i=m-1;i>=0;i--) {
                inv_fact[i] = inv_fact[i+1] * (i+1) % mod;
            }
        }
        long long res = 1;
        res = (res * inv_fact[sick[0]]) % mod;
        res = (res * inv_fact[n-sick.back()-1]) % mod;
        for (int i = 1;i<sick.size();i++) {
            int dist = sick[i] - sick[i-1]-1;
            if (dist == 0)
                continue;
            res = (res * modPow(2, dist-1, mod)) % mod;
            res = (res * inv_fact[dist]) % mod;
        }
        return (res * fact[n-sick.size()]) % mod;
    }
private:
    int modPow(int x, int y, int mod) {
        if (y == 0)
            return 1;
        long p = modPow(x,y/2,mod)%mod;
        p = (p*p)% mod;
        return y%2 ? (p*x) % mod : p;
    }
    long long binom_coeff(int n, int k) {
        return max(1LL, fact[n] * inv_fact[k] % mod * inv_fact[n-k] % mod);
    }
};