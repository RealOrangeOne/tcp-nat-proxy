#!/usr/bin/env bash

set -e

black --check tcp_nat_proxy.py
isort -c tcp_nat_proxy.py
flake8 tcp_nat_proxy.py --ignore=E128,E501
mypy --strict-optional --ignore-missing-imports tcp_nat_proxy.py
