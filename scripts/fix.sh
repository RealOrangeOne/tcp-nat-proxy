#!/usr/bin/env bash

set -e

black tcp_nat_proxy.py
isort -rc tcp_nat_proxy.py
