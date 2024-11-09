# Setup Script for Autogradescoper

## Overview

The `setup.sh` file is a shell script that installs the necessary software tools and libraries when building the Docker image for the Gradescope Autograder.

Typically, you do not need to modify the `setup.sh` file, but you may sometimes need to adjust it to install additional dependencies or libraries.

## A Typical Example

Below is a typical example of the `setup.sh` file for an R programming assignment. These scripts install the required software tools and libraries for the autograder and create a Python virtual environment to run the autograder.

```bash linenums="1"
#!/usr/bin/env bash

# Install Python, R, Git, and other necessary libraries.
apt-get install -y libxml2-dev libcurl4-openssl-dev libssl-dev
apt-get install -y python3 python3-pip python3-dev
apt-get install -y r-base
apt-get install -y git

# Create Python virtual environment
pip3 install virtualenv
virtualenv /venv
source /venv/bin/activate

# Install autogradescoper from GitHub
git clone https://github.com/hyunminkang/autogradescoper.git
cd autogradescoper
pip install -e .
```

This setup script assumes that the `autogradescoper` package is installed from the main branch of the [GitHub repository](https://github.com/hyunminkang/autogradescoper){:target="_blank"} to the `/autogradescoper` directory in the Docker image.

If you need to modify the autogradescoper source code, you can change the URL in the `git clone` command to your forked repository.

## Adding Additional R Packages

Sometimes, you may want to install additional R packages for the autograder. You can install R packages using the `install.packages()` function in R from the command line.

For example, to install the `package_name` R package, you can use the following command:

```bash linenums="1"
# Replace "package_name" with your desired R package name
R -e 'install.packages("package_name", repos="https://cran.rstudio.com")'
```
