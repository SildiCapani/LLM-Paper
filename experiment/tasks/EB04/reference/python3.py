MOD = 10 ** 9 + 7
m2 = {}
m1 = {}

def fac(n):
    if n not in m1: 
        r = 1 if n < 2 else n * fac(n - 1) % MOD
        m1[n] = r
    return m1[n]

def ifac(n):
    if n not in m2:
        r = pow(fac(n), -1, MOD)
        m2[n] = r
    return m2[n]

class Solution:
    def numberOfSequence(self, n, s):
        r = fac(n - len(s)) * ifac(s[0]) * ifac(n - s[-1] - 1) % MOD
        for g in [b - a - 1 for a, b in pairwise(s) if b - a > 1]:
            r *= ifac(g) * pow(2, g - 1, MOD)
            r %= MOD
        return r