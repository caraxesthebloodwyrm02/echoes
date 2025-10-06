#!/bin/bash

# Install test dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest tests/ -v --cov=./ --cov-report=term-missing --cov-report=xml:coverage.xml

# Check test coverage
coverage report --fail-under=80
