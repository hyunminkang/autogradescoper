## This is an example of incorrect answer
## loading functions from stats package is disallowed and should report an error
mypexp <- function(x, rate, lower.tail, log.p) {
  return(stats::pexp(x, rate, lower.tail, log.p))
}
