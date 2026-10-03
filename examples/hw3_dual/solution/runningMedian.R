## solution: runningMedian.R
## BIOSTAT 615 FA26 HW3 Problem 2 (R reference solution)
## Two binary heaps stored in preallocated numeric vectors; base package only.
## lo = max-heap of lower half, hi = min-heap of upper half.
## Invariant after each insert: nlo == nhi or nlo == nhi + 1.

runningMedian <- function(n, seed) {
  lo <- numeric(n); nlo <- 0L          ## max-heap (lower half)
  hi <- numeric(n); nhi <- 0L          ## min-heap (upper half)
  out <- numeric(n)
  x <- seed
  for (i in seq_len(n)) {
    x <- (69069 * x + 1) %% 4294967296
    u <- x / 4294967296

    ## 1) push u onto lo (max-heap sift-up)
    nlo <- nlo + 1L; lo[nlo] <- u; j <- nlo
    while (j > 1L) {
      p <- j %/% 2L
      if (lo[p] < lo[j]) { t <- lo[p]; lo[p] <- lo[j]; lo[j] <- t; j <- p }
      else break
    }

    ## 2) pop max of lo (sift-down), push onto hi (min-heap sift-up)
    v <- lo[1L]; lo[1L] <- lo[nlo]; nlo <- nlo - 1L
    j <- 1L
    repeat {
      l <- 2L * j; if (l > nlo) break
      r <- l + 1L
      big <- if (r <= nlo && lo[r] > lo[l]) r else l
      if (lo[big] > lo[j]) { t <- lo[big]; lo[big] <- lo[j]; lo[j] <- t; j <- big }
      else break
    }
    nhi <- nhi + 1L; hi[nhi] <- v; j <- nhi
    while (j > 1L) {
      p <- j %/% 2L
      if (hi[p] > hi[j]) { t <- hi[p]; hi[p] <- hi[j]; hi[j] <- t; j <- p }
      else break
    }

    ## 3) rebalance: if hi outgrew lo, move min of hi back to lo
    if (nhi > nlo) {
      v <- hi[1L]; hi[1L] <- hi[nhi]; nhi <- nhi - 1L
      j <- 1L
      repeat {
        l <- 2L * j; if (l > nhi) break
        r <- l + 1L
        sml <- if (r <= nhi && hi[r] < hi[l]) r else l
        if (hi[sml] < hi[j]) { t <- hi[sml]; hi[sml] <- hi[j]; hi[j] <- t; j <- sml }
        else break
      }
      nlo <- nlo + 1L; lo[nlo] <- v; j <- nlo
      while (j > 1L) {
        p <- j %/% 2L
        if (lo[p] < lo[j]) { t <- lo[p]; lo[p] <- lo[j]; lo[j] <- t; j <- p }
        else break
      }
    }

    out[i] <- if (nlo > nhi) lo[1L] else (lo[1L] + hi[1L]) / 2
  }
  out
}
