"""Large measurement inputs for the EffiBench-X tasks (one per task, fixed seed).

The dataset's test generators only produce small cases, so each workload is built here at
(or near) the upper bound of the task's constraints, in the exact stdin format of the
task's runner. Random structures are chosen so that typical solutions do real work
(duplicates, shared suffixes, near-palindromes) while trees stay shallow enough that
recursive solutions are not penalised by recursion limits.
"""
from __future__ import annotations

import random


def eb01(rng: random.Random) -> str:  # maximumTotalDamage(power)
    return ",".join(str(rng.randint(1, 300_000)) for _ in range(100_000))


def eb02(rng: random.Random) -> str:  # findKthSmallest(coins, k)
    coins = rng.sample(range(1, 26), 15)
    return ",".join(map(str, coins)) + " " + str(2 * 10**9)


def eb03(rng: random.Random) -> str:  # sumDigitDifferences(nums)
    return ",".join(str(rng.randint(10**8, 10**9 - 1)) for _ in range(100_000))


def eb04(rng: random.Random) -> str:  # numberOfSequence(n, sick)
    n = 100_000
    sick = sorted(rng.sample(range(n), 2_000))
    return f"{n} " + ",".join(map(str, sick))


def eb05(rng: random.Random) -> str:  # findSubtreeSizes(parent, s)
    n = 100_000
    parent = [-1] + [rng.randint(0, i - 1) for i in range(1, n)]
    s = "".join(rng.choice("abcde") for _ in range(n))
    return ",".join(map(str, parent)) + " " + s


def eb06(rng: random.Random) -> str:  # canMakePalindromeQueries(s, queries)
    n, half = 100_000, 50_000
    first = [rng.choice("abcdefghij") for _ in range(half)]
    second = first[::-1]
    for _ in range(20):  # a few mismatches so that answers differ
        second[rng.randrange(half)] = rng.choice("abcdefghij")
    s = "".join(first + second)
    queries = []
    for _ in range(100_000):
        a = rng.randrange(half); b = rng.randint(a, half - 1)
        c = rng.randint(half, n - 1); d = rng.randint(c, n - 1)
        queries.append(f"{a},{b},{c},{d}")
    return s + "\n" + ";".join(queries)


def eb07(rng: random.Random) -> str:  # maximumScoreAfterOperations(edges, values)
    n = 20_000
    edges = [(i, rng.randint(0, i - 1)) for i in range(1, n)]
    rng.shuffle(edges)
    edges = [(a, b) if rng.random() < 0.5 else (b, a) for a, b in edges]
    values = [rng.randint(1, 10**9) for _ in range(n)]
    return ",".join(map(str, values)) + "|" + ";".join(f"{a},{b}" for a, b in edges)


def eb08(rng: random.Random) -> str:  # numberOfPowerfulInt(start, finish, limit, s)
    limit = 6
    s = str(rng.randint(1, limit)) + "".join(str(rng.randint(0, limit)) for _ in range(3))
    return f"{rng.randint(1, 10**6)},{10**15},{limit},{s}"


def eb09(rng: random.Random) -> str:  # minimumCoins(prices)
    return ",".join(str(rng.randint(1, 100_000)) for _ in range(1_000))


def eb10(rng: random.Random) -> str:  # stringIndices(wordsContainer, wordsQuery)
    def words(total: int, count: int) -> list[str]:
        lengths = [rng.randint(1, 2 * total // count - 1) for _ in range(count)]
        scale = total / sum(lengths)
        return ["".join(rng.choice("abc") for _ in range(max(1, int(l * scale))))
                for l in lengths]
    return ",".join(words(500_000, 10_000)) + "\n" + ",".join(words(500_000, 10_000))


GENERATORS = {f"EB{i:02d}": f for i, f in enumerate(
    [eb01, eb02, eb03, eb04, eb05, eb06, eb07, eb08, eb09, eb10], 1)}


def make(task: str, seed: int = 20261025) -> str:
    return GENERATORS[task](random.Random(f"{seed}-{task}"))
