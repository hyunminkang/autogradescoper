## solution: running_median.py
## BIOSTAT 615 FA26 HW3 Problem 2 (python reference solution)
## Two heaps: max-heap of the lower half (negated), min-heap of the upper half.
## O(log n) per observation; O(n log n) total.

import heapq


def running_median(n, seed):
    n, seed = int(n), int(seed)
    lo, hi = [], []          # lo: max-heap via negation; hi: min-heap
    out = []
    x = seed
    for _ in range(n):
        x = (69069 * x + 1) % 4294967296
        u = x / 4294967296.0
        heapq.heappush(lo, -u)                     # push, then rebalance so that
        heapq.heappush(hi, -heapq.heappop(lo))     # len(lo) is len(hi) or len(hi)+1
        if len(hi) > len(lo):
            heapq.heappush(lo, -heapq.heappop(hi))
        out.append(-lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2.0)
    return out
