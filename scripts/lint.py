#!/usr/bin/env python3
"""
Cross-platform linting script for the project.
Can be run with: python scripts/lint.py
"""

import subprocess
import sys


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return whether it succeeded."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, check=True)
        print(f"✓ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed with exit code {e.returncode}")
        return False


def main() -> int:
    """Run all linting checks."""
    print("Starting linting checks...")

    checks = [
        (["ruff", "check", "."], "Ruff linter"),
        (["ruff", "format", "--check", "."], "Ruff formatter check"),
        (["mypy", "app/"], "MyPy type checker"),
    ]

    results = [run_command(cmd, desc) for cmd, desc in checks]

    if all(results):
        print("\n✓ All linting checks passed!")
        return 0
    else:
        print("\n✗ Some linting checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
