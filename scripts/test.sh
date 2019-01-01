#!/usr/bin/env bash

set -e

black --check tcp_nat_proxy.py
isort -c tcp_nat_proxy.py
flake8 tcp_nat_proxy.py
mypy --strict-optional --ignore-missing-imports tcp_nat_proxy.py
