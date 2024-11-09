# Use Case : Example Assignment

## Overview

This section describes the [autogradescoper example assignment available in GitHub repository](https://github.com/hyunminkang/autogradescoper/blob/main/examples){:target="_blank"} in detail. 
If you are interested in running the example assignment without understanding the details first, please see the [Quickstart](../quickstart.md) section.

The [Gradescope Autograder Documentation](https://gradescope-autograders.readthedocs.io/en/latest/){:target="_blank"} provides a comprehensive overview of how to use Gradescope. This documentation will not repeat the documentation, but rather focus on the specific use case of using `autogradescoper`.

## The Assignment : Specification

The objective of this example assignment is to reimplement 
the cumulative density function (CDF) of the expoential distribution from scratch. 

Let $x$ and $\lambda$ be positive real values. We want to evaluate the following quantity:

$$\Pr(X \leq x) = 1 - \exp(-\lambda x)$$

where $X$ is a random variable following the exponential distribution with rate parameter $\lambda$.
The key requirement is to implement the function robustly against possible numerical precision issues.

More specifically, the students are expected to write a function `mypexp(x, rate, lower.tail, log.p)` that reproduces the `pexp()` function in R only using the `base` package, where

- `x` : a positive real number (scalar), representing $x$ in the equation above.
- `rate` : a positive rate number (scalar), representing $\lambda$ in the equation above.
- `lower.tail` : a logical value (scalar), indicating whether to return $\Pr(X \leq x)$ (`TRUE`) or $\Pr(X > x)$ (`FALSE`).
- `log.p` : a logical value (scalar), indicating whether to return the natural logarithm of the probability density function (`TRUE`) or the probability density function itself (`FALSE`).

The students are expected to implement the function `mypexp()` in a file named `mypexp.R` and submit it to the autograder. It is important to maintain the precision of the output up to 8 digits, and it is allowed to use the `pexp()` function or any other functions outside the `base` package in the implementation. 

## The Assignment : A Sample Solution

Below is an example solution that implements the `mypexp()` function in R.

```r linenums="1"
mypexp <- function(x, rate, lower.tail, log.p) {
  if ( lower.tail ) { ## if lower.tail is TRUE
    if ( log.p ) {    ## if log.p is TRUE    
       if ( x*rate > 10 ) {      ## when x*rate is very large 
         return( -exp(-rate*x) ) ## use approximation: log(1-z) = -z, to avoid underflow
       }
       else {                            ## otherwise, 
         return( log(-expm1(-rate*x) ) ) ## use the exact formula
      }
    } else {          ## if log.p is FALSE
       return( -expm1(-rate*x) ) ## use expm1() to avoid numerical issues
    }
  } else {                ## if lower.tail is FALSE
    if ( log.p ) {        ## if log.p is TRUE
       return( -rate*x )  ## the formula is simple
    } else {              ## if log.p is FALSE
       return( exp(-rate*x) ) ## the formula is still simple
    }
  }
}
```

## Preparing Files for the Autograder 

The autograder used by `autogradscoper` typically has the following structure of input files:

```
|-- setup.sh
|-- run_autograder
|-- config/
| |-- config.yaml
| |-- config.prob.yaml
| `-- preload.baseonly.R
|-- solution/
| `-- [function_name].R 
`-- args/
  |-- test.1.args
  |-- test.2.args
  |-- ...
  `-- test.10.args
```

The `[function_name]` in this example is `mypexp`, because the students are expected to implement the `mypexp()` function in the `mypexp.R` file. 

These files can be found in the [GitHub repository](https://github.com/hyunminkang/autogradescoper/tree/main/examples/mypexp/){:target="_blank"}. We will explore the contents of each file one by one.

### setup.sh

The `setup.sh` file is a script that is used to build the Docker image for the autograder. It contains the commands to install necessary software tools and libraries based on a base image of Ubuntu 20.04. 

```bash linenums="1"
#!/usr/bin/env bash

## install python, R, git, and other necessary libraries.
apt-get install -y libxml2-dev libcurl4-openssl-dev libssl-dev
apt-get install -y python3 python3-pip python3-dev
apt-get install -y r-base
apt-get install -y git

## create python virtual environment
pip3 install virtualenv
virtualenv /venv
source /venv/bin/activate

## install autogradescoper from GitHub
git clone https://github.com/hyunminkang/autogradescoper.git
cd autogradescoper
pip install -e .
```

### run_autograder

The `run_autograder` is a script that is used to run the autograder. 
In `autogradescoper`, it simply runs the main `autogradescoper` command with specific arguments. 
Everything else is handled by the configuration files and the input files.

```bash linenums="1"
#!/usr/bin/env bash

## activate python virtual environment
source /venv/bin/activate

## run autogradescoper
## use --show-args and --show-details if you want to reveal input arguments and detailed output to students
autogradescoper eval_r_func_probset --show-args --show-details --show-errors
```

### Configuration files

The `config/` directory contains the configuration files for the autograder.

The `config/config.yaml` file contains the general configuration for the autograder, such as the name of the function to be evaluated and the name of the input arguments file.

```yaml linenums="1"
## config/config.yaml - contains the general configuration for the autograder
- func: "mypexp"      ## function to evaluate, e.g. mypexp() 
  filename: "mypexp"  ## submission file name, e.g. mypexp.R
  digits: 8  ## number of digits to compare the output
  config: /autograder/source/config/config.prob.yaml  ## problem-specific configuration
  preload_usr: /autograder/source/config/preload.baseonly.R ## script to load before loading submission file
# preload_sol: /autograder/source/config/preload.baseonly.R ## uncomment this line if you want to apply preload script in the solution file too
```

The `config/config.prob.yaml` file contains the problem-specific configuration for the autograder, such as the input argument for each test case and the time limit.

```yaml linenums="1"
## config/config.prob.yaml - contains the problem-specific configuration for the autograder
- args: /autograder/source/args/test.1.args
  maxtime: 1
- args: /autograder/source/args/test.2.args
  maxtime: 1
- args: /autograder/source/args/test.3.args
  maxtime: 1
- args: /autograder/source/args/test.4.args
  maxtime: 1
- args: /autograder/source/args/test.5.args
  maxtime: 1
- args: /autograder/source/args/test.6.args
  maxtime: 1
- args: /autograder/source/args/test.7.args
  maxtime: 1
- args: /autograder/source/args/test.8.args
  maxtime: 1
- args: /autograder/source/args/test.9.args
  maxtime: 1
- args: /autograder/source/args/test.10.args
  maxtime: 1
```

The `config/preload.baseonly.R` file contains the R script that is loaded before the submission file.
This file can be used in various purposes to limit the scope of students code to break the required conditions. For example, you can:

- Restrict students from using functions only from specific packages (e.g. `base` package)
    - For example, in case students are disallowed to use `lm()` function, for example, limiting the use of `stats` package can be a solution.
- Restrict students from installing custom packages
- Restrict students from call functions from disallowed packages using `::` operators.
- Restrict students from setting the random seed arbitrarily. 
- Define a wrapper function of the function to be implemented by students to check the correctness of implementation.

In this example assignment, the 
preload script restricts students from using any packages other than the `base` package.

```r linenums="1"
## config/preload.baseonly.R - contains the R script to load before the submission file
##
## This function allows students to use only specific packages
detach_disallowed_packages <- function(pkgnames) {
  # Get the list of all attached packages
  attached_packages <- search()

  # Keep only the base package + other essential packages
  allowed_package <- c(pkgnames,"package:utils", ".GlobalEnv","Autoloads")
  
  # Identify packages that are not the base package
  disallowed_packages <- setdiff(attached_packages, allowed_package)

  # Detach each disallowed package
  for (pkg in disallowed_packages) {
    try(detach(pkg, character.only = TRUE), silent = TRUE)
  }
}

## allow only base package
detach_disallowed_packages(c("package:base"))

## Redefine library() function to prevent loading additional packages
library <- function(...) {
  stop("Loading additional packages is not allowed.")
}

## Redefine require() function to prevent loading additional packages
require <- function(...) {
  stop("Loading additional packages is not allowed.")
}

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

## You may also redefine set.seed() function to prevent setting the random seed

## You may also define a wrapper function to evaluate user's function in more specific way.
## In this case, you need to specify the wrapper function as 'func' in the config.yaml file.
```

### Input Argument Files

The input arguments for each test case are stored in the `args/` directory.
Each line represents a single argument that is passed to the function to be evaluated.
The number of arguments must match to the number of arguments used in the function to be evaluated.

In this example assignment, the function `mypexp()` takes four arguments: `x`, `rate`, `lower.tail`, and `log.p`. Each argument must be specified in separate lines, in the format of `[type]:[value]` as in the following `args/test.1.args` file.

```plaintext linenums="1"
numeric:1 
numeric:10
numeric:TRUE
numeric:FALSE
```

Other than `numeric` types, you may also define `int`, `str`, `df` (for TSV), `rds` (for RDS), `eval` (for function). See [Creating a New Assignment](new_assignment.md) or the [Full documentation](../full/intro.md) to see more details.

### Solution File

The solution file contains the gold standard solution whose output used to compare output from the students' submissions. The instructors do not have to provide the expected output individually. Instead, the `autogradescoper` will run the solution file and student's submission file separately on the same input arguments, and compare the output to evaluate the correctness of the student's submission.

In `mypexp()` example, the function should behave exactly the same as `pexp()` function. Therefore, the solution file `solution/mypexp.R` simply calls the `pexp()` function from the `stats` package.

```r linenums="1"
## solution/mypexp.R - contains the solution file
mypexp <- function(x, rate, lower.tail, log.p) {
  ## simply calls pexp() function from stats package
  return(pexp(x, rate, lower.tail, log.p))
}
```

Note that this is NOT a correct solution, because the students are disallowed to use the `stats` package in their submission.

However, because the results of the function should exactly
match to the behavior of `stats::pexp()` function,
this will serve as a gold standard to compare the output with a submitted code.

The students will not be able to use stats::pexp() in their submission because
the preload script in the configuration prevents loading any functions outside the "base" package.

The autograder will run both the solution and submission code for each test case
and compare the output to check the correctness. 

### Creating a zip file for Autograder

To create a zip file for the autograder, you need to create a zip file that contains all the files and directories in the structure given previously:

```
|-- setup.sh
|-- run_autograder
|-- config/
| |-- config.yaml
| |-- config.prob.yaml
| `-- preload.baseonly.R
|-- solution/
| `-- [function_name].R 
`-- args/
  |-- test.1.args
  |-- test.2.args
  |-- ...
  `-- test.10.args
```

It is important NOT to include the parent directory in the zip file. When compressed these files should NOT be contained in another directory. 

## Testing the Example Assignment in Gradescope.

Using this Autograder file, you can create your course, create your assignment, and test your assignment as described in the [Quickstart](../quickstart.md) page.