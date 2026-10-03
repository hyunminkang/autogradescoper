## examples/v1_slow: correct but too slow -- linear-scan "dictionary".
## Mimics counting with parallel lists: O(n*k) total; fails the time limit
## at n = 10^6, k = 10^5.

def top_freq_items(n, k, m, seed):
    n, k, m, seed = int(n), int(k), int(m), int(seed)
    labels, counts = [], []
    x = seed
    for _ in range(n):
        x = (69069 * x + 1) % 4294967296
        lab = f"id{x % k}"
        if lab in labels:                 # O(k) scan per item -- the trap
            counts[labels.index(lab)] += 1
        else:
            labels.append(lab)
            counts.append(1)
    ranked = sorted(zip(labels, counts), key=lambda kv: (-kv[1], kv[0]))
    return [lab for lab, _ in ranked[:m]]
