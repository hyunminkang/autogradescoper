## solution: topFreqItems.R
## BIOSTAT 615 FA26 HW3 Problem 1 (R reference solution)
## table() builds a hash-based count in O(n); base package only.

topFreqItems <- function(n, k, m, seed) {
  x <- seed
  ids <- numeric(n)                     ## preallocate (never grow with c()!)
  for (i in seq_len(n)) {
    x <- (69069 * x + 1) %% 4294967296  ## exact in doubles: 69069*2^32 < 2^53
    ids[i] <- x %% k
  }
  cnt <- table(ids)                     ## hash-based counting, O(n)
  keys <- paste0("id", names(cnt))
  ## order by decreasing count, ties by byte-wise (C locale) lexicographic order
  o <- order(-as.vector(cnt), keys, method = "radix")
  keys[o][seq_len(min(m, length(keys)))]
}
