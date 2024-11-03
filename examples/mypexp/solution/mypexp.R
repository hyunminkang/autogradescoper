## NOTE: This is NOT a correct solution. 
##
## However, because the results of the function should exactly
## match to the behavior of stats::pexp() function,
## this will serve as a gold standard to compare the output with a submitted code.
##
## The students will not be able to use stats::pexp() in their submission because
## the preload script in the configuration prevents loading any functions outside the "base" package.
##
## The autograder will run both the solution and submission code for each test case
## and compare the output to check the correctness. 
mypexp <- function(x, rate, lower.tail, log.p) {
  return(pexp(x, rate, lower.tail, log.p))
}
