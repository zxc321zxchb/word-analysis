#!/usr/bin/env python3
"""Test runner script for Word Analysis Service."""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run tests for Word Analysis Service")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--cov", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--file", "-f", help="Run specific test file")

    args = parser.parse_args()

    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest"]

    # Add options
    if args.verbose:
        pytest_cmd.extend(["-vv"])
    else:
        pytest_cmd.extend(["-v"])

    # Add coverage
    if args.cov:
        pytest_cmd.extend([
            "--cov=src/doc_analysis",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])

    # Add markers
    markers = []
    if args.fast:
        markers.append("not slow")
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")

    if markers:
        pytest_cmd.extend(["-m", " and ".join(markers)])

    # Add specific file
    if args.file:
        pytest_cmd.append(args.file)

    # Check if pytest is available
    print("Checking dependencies...")
    try:
        import pytest
        print(f"✓ pytest {pytest.__version__} found")
    except ImportError:
        print("✗ pytest not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest pytest-cov"])
        print("✓ pytest installed")

    # Run tests
    success = run_command(pytest_cmd, "Test Suite")

    if success:
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)

        if args.cov:
            print("\nCoverage report generated:")
            print("  - Terminal: Displayed above")
            print("  - HTML: htmlcov/index.html")

        return 0
    else:
        print("\n" + "="*60)
        print("✗ Some tests failed!")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
