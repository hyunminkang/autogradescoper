# Installation

## Installation Not Required

To use the `autogradscoper` package, users do NOT need to install `autogradescoper` in their local computer.

The package is designed to be downloaded (via GitHub) and executed by the Gradescope Autograder. 

Users only need to prepare the Autograder files and upload them to the Gradescope platform.
See [Example Use Cases](../use_cases/example_assignment.md) or [Creating a New Assignment](../use_cases/new_assignment.md) for setup instructions.

## Installing `autogradescoper` for Development

If you want to develop the `autogradescoper` package, you can install the package from the GitHub repository.

```bash linenums="1"
# Install the `autogradescoper` package from GitHub
git clone https://github.com/hyunminkang/autogradescoper.git

# Change the directory to the `autogradescoper` package
cd autogradescoper

# Install the package in development mode
pip install -e .
```

This will allow you to modify the `autogradescoper` package and test the changes locally.

To check whether the package is installed correctly, you can run the following command:

```bash linenums="1"
autogradescoper 
```

Then the following message should appear:

```plaintext linenums="1"
Usage: autogradescoper <command> <args>, autogradescoper <command> -h to see arguments for each command
Available commands:
	eval_r_func_args
	eval_r_func_problem
	eval_r_func_probset
```