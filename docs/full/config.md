# Configuration files

The `config/` directory contains the configuration files for the autograder.

## The General Configuration File

### Overview 

The `config/config.yaml` file to specify the basic settings of the assignments, such as 
the function name used for evaluation or the filename students are required to submit. 

A typical example of the `config/config.yaml` file is shown below:

```yaml linenums="1"
- func: "[replace_me]"      ## change [replace_me] to the function to evaluate the code
  filename: "[replace_me]"  ## change [replace_me] to the R filename of the submission file (excluding .R)
  digits: [replace_me]      ## change [replace_me] to number of digits to compare the output
  config: /autograder/source/config/config.prob.yaml  ## problem-specific configuration
  preload_usr: /autograder/source/config/preload.baseonly.R  ## preload script for student submissions 
  preload_sol: /autograder/source/config/preload.baseonly.R  ## preload script for solution
```

### Required Fields

Here are required fields to include in the `config/config.yaml` file for each problem

- `func`: The name of the function to be evaluated. 
- `filename`: The filename students are required to submit.
- `config`: The path to the problem-specific configuration file.

#### Detail : `func` field

- `func` field typically should be identical to the name of the name of the function students are required to implement in the submission file.
    - For example, if the students are asked to implement a function named `mypexp()`, the field  `[replace_me]` with `myexp`. 
- However, sometimes you may want to take the output of the function students implemented and pass it to another function for evaluation. 
    - For example, you may ask students to implement `my_estimator(data)` function and evaluate the estimator by simulating the data such as `my_evaluator(nreps, nsamples, param1, param2)` function. In this case, you should specify the function name as `my_evaluator` and provide arguments corresponding to `my_evaluator()`.
    - See [Custom Evaluation Function](preload.md#custom-evaluation-function) for more details.

#### Detail : `filename` field

- The file name students are required to submit should end with `.R`. 
    - For example, if the students are asked to submit a file named `prob1.R`, you should replace `[replace_me]` with `prob1`.

#### Detail : `config` field

- The `config` field contains the path of problem-specific configuration file. 
- The path should be specified with `/autograder/source/` prefix, as the input files are located at `/autograder/source/` in the autograder container.
- Typically, recommend using `/autograder/source/config/config.prob.yaml` as the path.
- If you want to modify the name of the file, or have multiple problems in the assignments, you may replace this file name.

### Optional Fields

Here are optional fields to include in the `config/config.yaml` file for each problem

- `digits`: The number of digits to compare between the outputs of student's submission and the solution (default: 8)
- `format`: The format of the output values to compare (default: "g")
- `preload_usr`: The path to the preload script for student submissions.
- `preload_sol`: The path to the preload script for solutions.

#### Detail : `digits` field

- The `digits` field specifies the number of digits to compare the output. 
- For example, if you want to compare the output up to 8 digits, you should replace `[replace_me]` with `8`.
- See the details of the `format` field to understand more specific examples.

#### Detail : `format` field

- The `format` field specifies the format of the output values to compare. 
- The default format is `g`, which is typical way R prints out numeric values dynamic as scientific or fixed-point representation. 
- If you want to compare the output as a fixed floating point number, set `format` field it to `"f"`. 

For example:

- When `digits` is 8 and the output value is `1.2345678e-07`...
    - Using `format: "g"` (default) will compare the output as `1.2345678e-07`
    - Using `format: "f"` will compare the output as `0.00000012` (i.e. 8 digits below the decimal point).
- If you want to force the output to be compared as integer values...
    - Set `digits` to be `0` and select `format: "f"`. 
    - This will use 0 digits below the decimal point. 
  
#### Detail : `preload_usr` and `preload_sol` fields

- `preload_usr` specifies the preload script for student submissions, and `preload_sol` specifies the preload script for solutions.  
  - In most cases, you may want to use the same preload file for both submissions and solutions. 
  - If you want to use different preload files for submissions and solutions, you can specify different preload files for `preload_usr` and `preload_sol`.
  - You may choose to skip specifying the preload script in  `preload_sol`.

### Multiple Problems in a Single Assignment

While we recommend having a single problem in a single assignment, you can add multiple problems in a single assignment by adding additional configurations, by simpling adding additional elements in the list of `config/config.yaml` file.

```yaml linenums="1"
## example of multiple problems in a single assignment
- func: "[func_name_for_problem_1]"      
  filename: "[file_name_for_problem_1]"
  config: /autograder/source/config/config.prob1.yaml   ## configuration for problem 1
  preload_usr: /autograder/source/config/preload.prob1.R  ## preload script for problem 1 
  preload_sol: /autograder/source/config/preload.prob1.R  ## preload script for problem 1
- func: "[func_name_for_problem_2]"      
  filename: "[file_name_for_problem_2]"
  config: /autograder/source/config/config.prob2.yaml   ## configuration for problem 2
  preload_usr: /autograder/source/config/preload.prob2.R  ## preload script for problem 2 
  preload_sol: /autograder/source/config/preload.prob2.R  ## preload script for problem 2
- ## add more problems ....
```

## The Problem-Specific Configuration File

### Overview 

The `config/config.prob.yaml` file typically contains the problem-specific configuration for the autograder.
The YAML file should have a list of each test case, and each test case is typically considered to have 1
point. 

A typical example of a problem-specific configuration file is shown below:

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

### Required Fields

Each test case must have the following field:

- `args`: the path to the input arguments file for the test case.

#### Detail : `args` field

- The `args` field specifies the path to the input arguments file for the test case.
- The path should be specified with `/autograder/source/` prefix, as the input files are located at `/autograder/source/` in the autograder container.
- Typical name convention is to use `/autograder/source/args/test.1.args`, but you may replace this with other names, especially when there are multiple problems in the assignment.
- See the [Test Cases](args.md) section for more details on how to prepare the input arguments file for test cases.

### Optional Fields

Each test case may have the following field:

- `maxtime`: Maximum time allowed for the test case in seconds. (default: 10)
- `maxscore`: Maximum score for the test case. (default: 1)

#### Detail : `maxtime` field

- You may specify `maxtime` differently for each test case if the expected execution time varies by problem.
- The default value is 10 seconds.

#### Detail : `maxscore` field

- `maxscore` specifies the maximum score for the test case. 
- If this value is not set, the default value is 1. 
- If you want to assign different points to different test cases, you can specify the `maxscore` field.
- Note that, if `maxscore` is not 1, you MUST define your own custom evaluation function to return the score properly. See [Custom Scoring Function](preload.md#custom-scoring-function) for more details.