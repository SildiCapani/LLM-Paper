Measure memory allocation by building and traversing many perfect binary trees.

A *perfect binary tree of depth `d`* is a single leaf node for `d = 0`; otherwise it is a
node with two children, each a perfect binary tree of depth `d - 1`. The *check* of a tree
is its number of nodes, computed by traversing the tree.

Every tree must actually be allocated node by node and traversed. Do not compute the
check value arithmetically, and do not reuse, pool, or cache nodes or trees.

**Procedure**

1. Let `min_depth = 4` and `max_depth = max(min_depth + 2, N)`.
2. Build a tree of depth `max_depth + 1`, compute its check, print
   `stretch tree of depth <max_depth+1>\t check: <check>`, and discard the tree.
3. Build a *long-lived* tree of depth `max_depth` and keep it alive until step 5.
4. For each `depth` from `min_depth` to `max_depth` in steps of 2:
   let `iterations = 2^(max_depth - depth + min_depth)`; build `iterations` trees of
   depth `depth` one after another, computing the check of each and discarding it;
   print `<iterations>\t trees of depth <depth>\t check: <sum of checks>`.
5. Print `long lived tree of depth <max_depth>\t check: <check of the long-lived tree>`.

`\t` is a tab character. Each line of output ends with a newline.

**Example:** for `N = 10` the output is

```
stretch tree of depth 11	 check: 4095
1024	 trees of depth 4	 check: 31744
256	 trees of depth 6	 check: 32512
64	 trees of depth 8	 check: 32704
16	 trees of depth 10	 check: 32752
long lived tree of depth 10	 check: 2047
```
