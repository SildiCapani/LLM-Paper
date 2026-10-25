import sys


class Node:
    __slots__ = ("left", "right")

    def __init__(self, left, right):
        self.left = left
        self.right = right


def make(depth):
    if depth == 0:
        return Node(None, None)
    return Node(make(depth - 1), make(depth - 1))


def check(node):
    if node.left is None:
        return 1
    return 1 + check(node.left) + check(node.right)


def main():
    n = int(sys.argv[1])
    min_depth = 4
    max_depth = max(min_depth + 2, n)
    stretch = max_depth + 1
    print(f"stretch tree of depth {stretch}\t check: {check(make(stretch))}")
    long_lived = make(max_depth)
    for depth in range(min_depth, max_depth + 1, 2):
        iterations = 1 << (max_depth - depth + min_depth)
        total = sum(check(make(depth)) for _ in range(iterations))
        print(f"{iterations}\t trees of depth {depth}\t check: {total}")
    print(f"long lived tree of depth {max_depth}\t check: {check(long_lived)}")


main()
