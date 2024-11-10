testlm <- function(y, X) {
  as.numeric(lm(y~X)$coef)
}
