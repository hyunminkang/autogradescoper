detach_non_base_packages <- function() {
  # Get the list of all attached packages
  attached_packages <- search()

  # Keep only the base package
  allowed_package <- c("package:base",".GlobalEnv","Autoloads")
  
  # Identify packages that are not the base package
  non_base_packages <- setdiff(attached_packages, allowed_package)

  # Detach each non-base package
  for (pkg in non_base_packages) {
    try(detach(pkg, character.only = TRUE), silent = TRUE)
  }
}

detach_non_base_packages()

library <- function(...) {
  stop("Loading additional packages is not allowed.")
}

require <- function(...) {
  stop("Loading additional packages is not allowed.")
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
