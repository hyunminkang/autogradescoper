#!/usr/bin/env bash
# Runs once when Gradescope builds the autograder (default base image; no
# custom Docker needed). R assignments.
set -e
apt-get update
apt-get install -y r-base python3 python3-pip python3-venv
python3 -m venv /venv
source /venv/bin/activate
pip install autogradescoper
