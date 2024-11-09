# Use Case : Creating a New Assignment

## Start from the Example Assignment

To create your own assignment, the easiest way is to start from the [Example Assignment](example_assignment.md) we used in the previous section.

Below is the directory structure of the new example assignment. Each file is commented with the changes you may want to make for the new assignment. The specific changes to be made are described in the following sections.

```
|-- setup.sh                # no change needed (unless you need to install additional packages)
|-- run_autograder          # no change needed (unless you want to change what students can view)
|-- config/
| |-- config.yaml           # change 'func' and 'filename' fields
| |-- config.prob.yaml      # change 'maxtime' fields if needed
| `-- preload.baseonly.R    # no change needed (unless you want to allow additional packages)
|-- solution/
| `-- [function_name].R     # change this to your solution
`-- args/
  |-- test.1.args           # change to the arguments you want to test
  |-- test.2.args           # ...
  |-- ...
  `-- test.10.args
```

Note that these autograder source files will be located at `/autograder/source/` in the autograder container.

## setup.sh

Typically, you do not need to modify the `setup.sh` file. However, if you want to install additional R packages, see the commented lines at the end of the example below.

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

## NOTE: if you need to install additional R packages, add them here
## Example command may look like this:
## R -e 'install.packages("package_name", repos="http://cran.r-project.org")'
```

## run_autograder

The `run_autograder` simply runs the main `autogradescoper` command with specific arguments.

```bash linenums="1"
#!/usr/bin/env bash

## activate python virtual environment
source /venv/bin/activate

## run autogradescoper
## use --show-args and --show-details if you want to reveal input arguments and detailed output to students
autogradescoper eval_r_func_probset --show-args --show-details --show-errors
```

Typically, you do not need to modify this file. However, you may want to selectively turn on the following arguments based on your needs (default is off):

- `--show-args`: show the input arguments to the students.
- `--show-details`: show the detailed output to the students.
- `--show-errors`: show the error messages to the students.

It is strongly recommended to turn on `--show-errors` to help students debug their code. Showing the detailed output (`--show-details`) and test arguments (`--show-args`) may help students understand their issues better, but it may allow students to take advantage of the test cases. Depending on the nature of the assignment, you may want to turn them off.

Finally, there is a special option to turn on:

- `--skip-solution`: skip running the solution code. See the [Custom Scoring Function](#custom-scoring-function) section for more details.

Note that this option requires using a [Custom Scoring Function](#custom-scoring-function). The custom evaluation script must return the score and details in the output.

## Configuration Files

The `config/` directory contains the configuration files for the autograder.

### General Configuration File

You will need to modify the `config/config.yaml` file to specify the function to be evaluated and the filename of the submission file at the minimum.

```yaml linenums="1"
## config/config.yaml - contains the general configuration for the autograder
- func: "[replace_me]"      ## change [replace_me] to the function to evaluate the code
  filename: "[replace_me]"  ## change [replace_me] to the R filename of the submission file (excluding .R)
  digits: [replace_me]      ## change [replace_me] to number of digits to compare the output
# format: "f"               ## uncomment this line if you want to compare the output as a fixed floating point number
  config: /autograder/source/config/config.prob.yaml  ## problem-specific configuration
  preload_usr: /autograder/source/config/preload.baseonly.R  ## preload file for student submissions 
  preload_sol: /autograder/source/config/preload.baseonly.R  ## in most cases, you may want to use the same preload file for both submissions and solutions
## NOTE: If you have multiple problems in the same assignment, you can add additional configurations here
## Uncomment the following lines if you want to have multiple problems
## - func: "[func_name_prob2]"     ## change [func_name_prob2] to the function to evaluate the code
##   filename: "[filename_prob2]"  ## change [filename_prob2] to the R filename of the submission file (excluding .R)
##   digits: 8  ## number of digits to compare the output
##   config: /autograder/source/config/config.prob2.yaml  ## problem-specific configuration
##   preload_usr: /autograder/source/config/preload.baseonly.R  ## you may use the same preload script or change it
##   preload_sol: /autograder/source/config/preload.baseonly.R  
```

Key considerations when modifying the `config/config.yaml` file:

- The function name should match the function students are required to implement.
    - A different function name can be specified if the output of the student's function is passed to another function for evaluation. See the [Custom Evaluation Function](#custom-evaluation-function) section for more details.
- The filename should end with `.R`.
- The `digits` field specifies the number of digits to compare the output.
- The `format` field specifies the format of the output values to compare.
- `preload_usr` and `preload_sol` specify the preload scripts for submissions and solutions.
- For multiple problems, add additional configurations by uncommenting the lines after `## NOTE:`.

### Problem-Specific Configuration File

The `config/config.prob.yaml` file contains the problem-specific configuration for the autograder.
The YAML file should have a list of each test case, and each test case is typically considered to have 1
point. 

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

Each test case should have the following fields:
- `args`: the path to the input arguments file for the test case.
- `maxtime`: the maximum time allowed for the test case in seconds.
- `maxscore`: (optional) the maximum score for the test case.

### Preload Script

The preload script loads necessary R packages and functions before running the student's code.

#### Detaching Disallowed Packages

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

#### Preventing Users from Loading Additional Packages

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

#### Preventing Disallowed Patterns of Use

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

#### Fixing Random Seed

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

#### Custom Evaluation Function

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

#### Custom Scoring Function

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

If the score is not 0 to 1 scale, modify the `config/config.prob.yaml` file to include the `maxscore` field for each test case.

```yaml linenums="1"
## example config/config.prob.yaml 
- args: /autograder/source/args/test.1.args
  maxtime: 10
  maxscore: 2
- args: /autograder/source/args/test.2.args
  ...
```

## Specifying Input Arguments

The `args/` directory typically contains the input arguments for each test case.
For each test case. `test.i.args` file contains the input arguments for the test case `i`.
Each line of the file should contain the input arguments for the test case, in the format of
`{type}:{value}` as follows:

```plaintext linenums="1"
numeric:1 
numeric:10
numeric:TRUE
numeric:FALSE
```

Sometimes, the input argument may contain a string. In this case, you can specify the input argument without quote as follows:

```plaintext linenums="1"
str:hello
str:world
```

If you want to pass a TSV file as an input to load as a dataframe, use `df` type as follows:

```plaintext linenums="1"
df:/autograder/source/args/test.1.tsv
``` 

Typically, locating the input files in the `args/` directory is recommended.
The path should be specified with '/autograder/source/' prefix, as the input files are located at `/autograder/source/` in the autograder container.

For other data types, such as matrix or other objects, it is recommended to use `rds` as follows

```plaintext linenums="1"
rds:/autograder/source/args/test.1.rds
```

The `rds` type is used to load the R object saved in the `.rds` file format. These files can be created using the `saveRDS()` function in R. 
The autograder will load these arguments using the `readRDS()` function in R when evaluating the function with the input arguments.

## Preparing the Solution Files

The solution files are typically located in the `solution/` directory, with the filename specified in the `config/config.yaml` file. If you turn on `--skip-solution` option in the `run_autograder` script, the solution files will not be needed.

## Debugging the Autograder

The [Gradescope Autograder Documentation](https://gradescope-autograders.readthedocs.io/en/latest/){target="_blank"} provides a detailed guide on setting up the Autograder. If you encounter any technical issues, this documentation provides a comprehensive details on the autograder setup.

If the autograder does not behave as expected, typical way to debug the code is to run the autograder in the container and connect via SSH. See [Gradescope Debugging via SSH](https://gradescope-autograders.readthedocs.io/en/latest/ssh/). See also [Additional Troubleshooting Tips](https://gradescope-autograders.readthedocs.io/en/latest/troubleshooting/) for any other issues you may encounter.



