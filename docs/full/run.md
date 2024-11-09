# Startup Script for Autogradescoper

## Overview 

The `run_autograder` script runs the main `autogradescoper` command with specific settings.
This script typically runs on the Gradescope platform for each student's submission.
You may also want to run this script locally to test the autograder.

## A Typical Example

If you are unsure how to prepare the `run_autograder` script, you can use the following template:

```bash linenums="1"
#!/usr/bin/env bash

## activate python virtual environment
source /venv/bin/activate

## run autogradescoper, showing input arguments, detailed output, and error messages to students
autogradescoper eval_r_func_probset --show-args --show-details --show-errors
```

## Options to Show Output to Students

You may want to selectively turn on the following arguments based on your needs (default is off):

- `--show-args`: Show the input arguments to the students.
- `--show-details`: Show the detailed output to the students.
- `--show-errors`: Show the error messages to the students.

It is strongly recommended to turn on `--show-errors` to help students debug their code.
Showing the detailed output (`--show-details`) and test arguments (`--show-args`) may help students understand their issues better, but it may allow students to take advantage of the test cases. Depending on the nature of the assignment, you may want to turn them off.

## Options for Custom Scoring Function 

If you want to customize the scoring function (instead of comparing the output to the solution), you need to turn on the following option:

- `skip-solution`: Skip running the solution code. 

If you use `skip-solution`, you need to provide a custom evaluation function that returns the score and details in the output. You do not need to provide solution files in this case.

Note that this option requires using a [Custom Scoring Function](#custom-scoring-function). The custom evaluation script must return the score and details in the output.
