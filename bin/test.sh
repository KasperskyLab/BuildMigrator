#!/bin/bash

set -e
SCRIPT_DIR=`dirname "$0"`
python -m unittest discover -v -s "$SCRIPT_DIR/../tests"
