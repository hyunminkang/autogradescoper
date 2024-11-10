predictlm <- function(y, X) {
  as.numeric(lm(y~X)$fitted.values)
}
