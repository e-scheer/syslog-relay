#!/bin/bash

sudo apt install python3-pip
pip install virtualenv

virtualenv venv
source venv/bin/activate

pip install -r requirements.txt