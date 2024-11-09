# The Preload Script

## Overview 

The preload script is an important script that loads necessary 
R packages and functions before running the student's code. It contains the code to
override some functions to help students conform their submissions to the requirements.

The preload script has a large amount of flexibility in terms of what you can do. 
Here we will break down into parts to explain the key components of the default preload script
provided with the [Example Assignment](../use_cases/example_assignment.md). 
We will also provide additional examples on implementing custom evaluation functions, too.

The following part of the preload script is to prevent students from using 
disallowed packages and functions. If students are only allowed to use the `base` package,
you can use the following code to detach all non-base packages.

## Detaching Disallowed Packages

```R linenums="1"
## Part of the preload script to prevent users from using disallowed packages
detach_disallowed_packages <- function(pkgnames) {
  attached_packages <- search()
  allowed_package <- c(pkgnames,"package:utils", ".GlobalEnv","Autoloads")
  disallowed_packages <- setdiff(attached_packages, allowed_package)
  for (pkg in disallowed_packages) {
    try(detach(pkg, character.only = TRUE), silent = TRUE)
  }
}

detach_disallowed_packages(c("package:base"))
```

If you want to allow students to use `stats` packages, you may want to modify the last line to the following:

```R linenums="1"
detach_disallowed_packages(c("package:base", "package:stats"))
```

## Preventing Users to Load Additional Packages

The following code snipplet prevents students from 
loading additional packages using `library()` or `require()` functions.

```R linenums="1"
## Redefine library() function to prevent loading additional packages
library <- function(...) {
  stop("Loading additional packages is not allowed.")
}

## Redefine require() function to prevent loading additional packages
require <- function(...) {
  stop("Loading additional packages is not allowed.")
}
```

## Preventing Disallowed Patterns of Use

Even if disallowed packages are detached, the students may still try to access the functions
using `::` operator. For example, `stats::lm()` will still work even if the `stats` package is detached.

To prevent such a loophole, we can scan a patterns of use of `::` or `:::` operators in the submission file
before loading them. To do this, we can redefine the `source()` function in R as follows.

```R linenums="1"
## Redefine source() function to check a disallowed pattern in the submitted file
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
```

The above code can be extended to detect more specific patterns. 
For example, if certain expressions are required or disallowed in the student's submission, they can be added
to the `source()` function above.

## Fixing Random Seed

For problems that require random number generation, 
you may want to fix the random seed to make the results reproducible, and prevent students from
using arbitrary random seeds. 

```R linenums="1"
## set a random seed
set.seed(2024)
## disable setting the random seed by users
set.seed <- function(seed) { 
    # do nothing
}
```

## Custom Evaluation Function

Typically, the function students are asked to implement returns the output values that can be evaluated directly. However, sometimes you may want to evaluate the output values in a more specific way. In such cases, you can define a custom evaluation function in the preload script.

For example, suppose that students are asked to implement a function `predict(data, coef)` that returns the predicted values. You may want to return the mean squared error (MSE) between the true values and the predicted values. In this case, you can define a custom evaluation function as follows:

```R linenums="1"
## custom evaluation function for evaluating the output
evaluate_predict <- function(data, coef, true_values) {
    predicted <- predict(data, coef)
    mse <- mean((predicted - true_values)^2)
    return(mse)
}
```

In this case, the configuration file should have `evaluate_predict` as the function name, and 
`predict` as the file name, asking students to submit `predict.R` that contains the `predict()` function as follows:

```yaml linenums="1"
## example config/config.yaml
- func: "evaluate_predict" 
  filename: "predict" 
  ...
```

## Custom Scoring Function

By default, the autograder runs the solution and student's code, and compares the output values to determine the score. However, sometimes you may want to evaluate the output values in a more specific way and assign a score based on the evaluation. In such cases, you can define a custom scoring function in the preload script. 

NOTE that `--skip-solution` option must be turned on in the `run_autograder` script to skip running the solution code.

In order to use this feature, your custom evaluation function should return a list that contains the following attributes:

- `score`: the score for the test case
- `details`: the output message to be shown to the students.

For example, in the example above, you may want to score the test case based on the MSE between the true values and the predicted values quantitatively. In this case, you can define a custom scoring function as follows:

```R linenums="1"
## custom evaluation function for evaluating the output
evaluate_predict <- function(data, coef, true_values) {
    predicted <- predict(data, coef)
    mse <- mean((predicted - true_values)^2)
    score <- 1 - mse / sum(true_values^2)
    return(list(score = score, details = paste0("MSE = ", mse, ", Sum of True Values = ", sum(true_values^2))))
}
```

If the score is not 0 to 1 scale, you will need to modify the `config/config.prob.yaml` file to include the `maxscore` field for each test case as follows:

```yaml linenums="1"
## example config/config.prob.yaml 
- args: /autograder/source/args/test.1.args
  maxtime: 10
  maxscore: 2
- args: /autograder/source/args/test.2.args
  ...
```