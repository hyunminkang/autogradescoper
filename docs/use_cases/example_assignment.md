# Use Case : Example Assignment

## Overview

This section describes the [autogradescoper example assignment available in GitHub repository](https://github.com/hyunminkang/autogradescoper/blob/main/examples){:target="_blank"} in detail. 
If you are interested in running the example assignment without understanding the details first, please see the [Quickstart](../quickstart.md) section.

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

```r
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

```bash
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

```bash
#!/usr/bin/env bash

## activate python virtual environment
source /venv/bin/activate

## run autogradescoper
## use --show-args and --show-details if you want to reveal input arguments and detailed output to students
autogradescoper eval_r_func_probset --show-args --show-details --show-errors
```

(To be continued...)