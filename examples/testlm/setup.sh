#!/usr/bin/env bash

# or you can do it the slow way...
apt-get install -y libxml2-dev libcurl4-openssl-dev libssl-dev
apt-get install -y python3 python3-pip python3-dev
apt-get install -y r-base
apt-get install -y git

pip3 install virtualenv
virtualenv /venv
source /venv/bin/activate
git clone https://github.com/hyunminkang/autogradescoper.git
cd autogradescoper
pip install -e .
