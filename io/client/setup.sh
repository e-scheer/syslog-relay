#!/bin/bash

sudo apt install python3-pip
pip install virtualenv

virtualenv .venv

echo -e "\n"
echo "Run 'source .venv/bin/activate' to enter the virtual environment."
echo "Do not forget to install required packages using 'pip install -r requirements.txt'."