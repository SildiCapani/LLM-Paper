class Solution:
    def numberOfPowerfulInt(self, start: int, finish: int, limit: int, s: str) -> int:
        startStr, finishStr = str(start - 1), str(finish)

        def calculate(num: str) -> int:
            if len(num) < len(s): return 0
            if len(num) == len(s):
                return 1 if num >= s else 0
            lengthDiff = len(num) - len(s)
            substr, ans = num[lengthDiff:], 0
            for idx in range(lengthDiff):
                if limit < (ord(num[idx]) - ord('0')):
                    ans += (limit + 1) ** (lengthDiff - idx)
                    return ans
                ans += ((ord(num[idx]) - ord('0')) * ((limit + 1) ** (lengthDiff - 1 - idx)))
            if substr >= s: ans += 1
            return ans

        return calculate(finishStr) - calculate(startStr)