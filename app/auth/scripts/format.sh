#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place auth --exclude="__init__.py, base_class.py"
black auth
isort auth