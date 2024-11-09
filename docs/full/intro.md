# Full Documentation: Introduction

## Overview

This documentation provides a step-by-step guide to setting up an autograder for programming assignments using the `autogradescoper` package. The autograder is designed to work with Gradescope, an online platform for grading programming assignments.

## Gradescope Autograder Documentation

The [Gradescope Autograder Documentation](https://gradescope-autograders.readthedocs.io/en/latest/){target="_blank"} offers a comprehensive guide on setting up the autograder.

## Types of Assignments for Autogradescoper

The [Autogradescoper](../index.md) package streamlines the setup of the Gradescope autograder for various R programming assignments.

`Autogradescoper` is ideal for:

* Assignments in the R programming language.
* Tasks requiring students to implement specific functions.
* Assignments that can be automatically graded using predefined test cases.
* Projects with constraints such as execution time limits or restricted use of certain packages.

### Typical Example Assignments

A typical assignment is structured as follows:

* A single assignment usually contains one problem.
    - For multiple problems, see [Configuration](config.md) for details on adding additional problems.
* There is a 'correct' solution used to evaluate the student's submission.
    - The default evaluation mode compares the student's function output to the prepared solution's output.
    - For assignments without a 'correct solution' (e.g., graded on output accuracy), use the `--skip-solution` option. See [Custom Scoring Function](preload.md#custom-scoring-function) for more details.

This documentation explains how to set up the autograder for these types of assignments.

## Installation Not Required

Users do NOT need to install the `autogradescoper` package. The package is designed to be downloaded (via GitHub) and executed by the Gradescope Autograder. Users need to prepare the autograder files and upload them to the Gradescope platform. See [Example Use Cases](../use_cases/example_assignment.md) or [Creating a New Assignment](../use_cases/new_assignment.md) for setup instructions.

## The Autograder Files

According to the [Gradescope Autograder Documentation](https://gradescope-autograders.readthedocs.io/en/latest/){target="_blank"}, the Gradescope Autograder requires the following files:

```plaintext linenums="1"
|-- setup.sh            ## setup script - run once to build the Docker image    
`-- run_autograder      ## startup script - run for each student submission    
```

The `autogradescoper` package assumes additional files for R programming assignments. The recommended structure is:

```plaintext linenums="1"
|-- setup.sh                
|-- run_autograder          
|-- config/
| |-- config.yaml      ## configuration file     
| |-- config.prob.yaml      
| `-- preload.baseonly.R 
|-- solution/
| `-- ${filename}.R    ## change ${filename} according to the assignment.
`-- args/
  |-- test.1.args        
  |-- test.2.args         
  |-- ...
  `-- test.${N}.args
```

## Structure of the Documentation

The rest of this documentation explains how to prepare the autograder files for an R programming assignment. It also provides detailed instructions on testing and debugging the autograder on the Gradescope platform.