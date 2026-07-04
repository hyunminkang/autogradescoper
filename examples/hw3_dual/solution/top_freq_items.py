## solution: top_freq_items.py
## BIOSTAT 615 FA26 HW3 Problem 1 (python reference solution)
## Uses a hash table (Counter/dict) for O(n + k log k) total time.

from collections import Counter


def top_freq_items(n, k, m, seed):
    n, k, m, seed = int(n), int(k), int(m), int(seed)
    cnt = Counter()
    x = seed
    for _ in range(n):
        x = (69069 * x + 1) % 4294967296
        cnt[f"id{x % k}"] += 1                      # O(1) hash update
    ranked = sorted(cnt.items(), key=lambda kv: (-kv[1], kv[0]))
    return [key for key, _ in ranked[:m]]
