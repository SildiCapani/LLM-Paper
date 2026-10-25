static auto _ = [](){
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cout.tie(nullptr);
    return nullptr;
}();
class Solution {
public:
    long long sumDigitDifferences(vector<int>& nums) {
        int cntDigits[11][10];
        for (auto n : nums) {
            int i = 0;
            while (n) {
                cntDigits[i][n % 10]++;
                n /= 10;
                i++;
            }
        }

        long long ans = 0;
        for (int i = 0; i < 11; i++) {
            for (int j = 0; j < 10; j++) {
                if (cntDigits[i][j] == 0) continue;
                long long sum = 0;
                for (int k = j + 1; k < 10; k++) {
                    sum += cntDigits[i][k];
                }
                ans += cntDigits[i][j] * sum;
            }
        }

        return ans;
    }
};