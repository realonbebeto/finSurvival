#!/usr/bin/env bash

set -x

mypy auth
black auth --check
isort --recursive --check-only auth
flake8