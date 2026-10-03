## examples/v1_slow: correct but too slow -- re-sorts after every observation.
## O(n^2) total element operations; fails the time limit at n = 50,000.

def running_median(n, seed):
    n, seed = int(n), int(seed)
    xs, out = [], []
    x = seed
    for _ in range(n):
        x = (69069 * x + 1) % 4294967296
        xs.append(x / 4294967296.0)
        s = sorted(xs)                    # O(i log i) every single step
        mid = len(s) // 2
        out.append(s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2.0)
    return out
