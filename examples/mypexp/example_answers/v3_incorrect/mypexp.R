## This is an example of incorrect answer
## Only a subset of test cases will give correct answers
mypexp <- function(x, rate = 1, lower.tail = TRUE, log.p = FALSE) {
  # Calculate the probability
  p <- 1 - exp(-rate * x)
  
  # Adjust for lower.tail argument
  if (!lower.tail) {
    p <- 1 - p
  }
  
  # Adjust for log.p argument
  if (log.p) {
    p <- log(p)
  }
  
  return(p)
}
