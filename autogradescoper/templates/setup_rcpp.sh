#!/usr/bin/env bash
# Runs once when Gradescope builds the autograder (default base image; no
# custom Docker needed). C++ (Rcpp) assignments: needs R + a compiler + Rcpp.
set -e
apt-get update
apt-get install -y r-base r-base-dev build-essential python3 python3-pip python3-venv
Rscript -e 'if (!requireNamespace("Rcpp", quietly=TRUE)) install.packages("Rcpp", repos="https://cloud.r-project.org")'
python3 -m venv /venv
source /venv/bin/activate
pip install autogradescoper
