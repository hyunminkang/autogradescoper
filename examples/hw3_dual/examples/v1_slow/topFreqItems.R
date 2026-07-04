## examples/v1_slow: correct but too slow -- a named list used as a dictionary.
## Each `cnt[[lab]]` lookup scans all names: O(n*k) total.
## Fails the time limit at n = 10^6, k = 10^5 (Topic 4, Part 2).

topFreqItems <- function(n, k, m, seed) {
  x <- seed
  cnt <- list()
  for (i in seq_len(n)) {
    x <- (69069 * x + 1) %% 4294967296
    lab <- paste0("id", x %% k)
    if (is.null(cnt[[lab]])) {           ## linear scan over names -- the trap
      cnt[[lab]] <- 1
    } else {
      cnt[[lab]] <- cnt[[lab]] + 1       ## and the list may be copied, too
    }
  }
  keys <- names(cnt)
  vals <- unlist(cnt)
  o <- order(-vals, keys, method = "radix")
  keys[o][seq_len(min(m, length(keys)))]
}
