## examples/v1_slow: correct but too slow -- re-sorts after every observation.
## O(n^2 log n); fails the time limit at n = 50,000.

runningMedian <- function(n, seed) {
  xs <- numeric(0)
  out <- numeric(n)
  x <- seed
  for (i in seq_len(n)) {
    x <- (69069 * x + 1) %% 4294967296
    xs <- c(xs, x / 4294967296)          ## grows the vector AND
    s <- sort(xs)                        ## re-sorts, every step
    mid <- length(s) %/% 2L
    out[i] <- if (length(s) %% 2L == 1L) s[mid + 1L] else (s[mid] + s[mid + 1L]) / 2
  }
  out
}
