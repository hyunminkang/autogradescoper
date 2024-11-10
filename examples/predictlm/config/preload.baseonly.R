detach_disallowed_packages <- function(pkgnames) {
  attached_packages <- search()
  allowed_package <- c(pkgnames,"package:utils", ".GlobalEnv","Autoloads")
  disallowed_packages <- setdiff(attached_packages, allowed_package)
  for (pkg in disallowed_packages) {
    try(detach(pkg, character.only = TRUE), silent = TRUE)
  }
}

detach_disallowed_packages(c("package:base", "package:stats"))

library <- function(...) {
  stop("Loading additional packages is not allowed.")
}

require <- function(...) {
  stop("Loading additional packages is not allowed.")
}

evalpredictlm <- function(y, X) {
  yhat <- predictlm(y, X)
  r <- cor(y, yhat)
  return(list(score=r*r, details=paste0("cor = ", r)))
}

source <- function(file) {
  file_content <- readLines(file)
  # Check if the file contains "::" or ":::"
  contains_double_colon <- any(grepl("::", file_content))
  contains_triple_colon <- any(grepl(":::", file_content))

  if ( contains_double_colon || contains_triple_colon ) {
    stop("Use of :: or ::: is not allowed")
  }

  expr <- parse(file)
  eval(expr, envir = globalenv())
}
