#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place gateway --exclude="__init__.py, base_class.py"
black gateway
isort gateway