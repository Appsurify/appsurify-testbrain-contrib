#!/usr/bin/env bash

poetry run pytest --junit-xml=reports/junit-macOS-PY3.12.xml
#poetry run pytest -v --junitxml=reports/junit-macOS-PY3.12.xml --cov-report xml:reports/coverage-macOS-PY3.12.xml --cov=./src/testbrain ./tests/

poetry run pytest --no-header --no-summary -q --junit-xml=reports/junit-macOS-PY3.12.xml -o junit_suite_name=example -o junit_family=xunit1 tests/example
poetry run pytest --no-header --no-summary --junit-xml=reports/junit-macOS-PY3.12.xml -o junit_suite_name=example -k "example or usage"
