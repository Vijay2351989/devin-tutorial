#!/bin/bash
# Linting script for the project

echo "Running Ruff linter..."
ruff check .

echo "Running Ruff formatter check..."
ruff format --check .

echo "Running MyPy type checker..."
mypy app/

echo "Linting complete!"
