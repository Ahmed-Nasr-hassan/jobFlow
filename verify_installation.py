#!/usr/bin/env python3
"""Script to verify JobFlow installation and package structure.

Run this after installing the package to verify everything works.
"""

import sys


def verify_installation():
    """Verify that JobFlow is properly installed."""
    print("Verifying JobFlow installation...")
    print("=" * 60)

    # Test 1: Import root package
    try:
        import jobflow
        print("✓ Root package 'jobflow' imports successfully")
        print(f"  Version: {jobflow.__version__}")
        print(f"  Exports: {len(jobflow.__all__)} items")
    except ImportError as e:
        print(f"✗ Failed to import jobflow: {e}")
        print("  Make sure you've run: pip install -e .")
        return False

    # Test 2: Import key components
    try:
        from jobflow import RunScriptUseCase
        from jobflow import ScriptConfig
        from jobflow import LocalSubprocessExecutor
        from jobflow import StdoutLogSink
        from jobflow import FileProvider
        from jobflow import LogSink
        print("✓ All key components import successfully")
    except ImportError as e:
        print(f"✗ Failed to import components: {e}")
        return False

    # Test 3: Import from subpackages (should also work)
    try:
        from jobflow.application import RunScriptUseCase
        from jobflow.domain import ScriptConfig
        from jobflow.infrastructure import LocalSubprocessExecutor
        print("✓ Subpackage imports work correctly")
    except ImportError as e:
        print(f"✗ Failed to import from subpackages: {e}")
        return False

    # Test 4: Check package structure
    try:
        import jobflow.application
        import jobflow.domain
        import jobflow.infrastructure
        print("✓ Package structure is correct")
    except ImportError as e:
        print(f"✗ Package structure issue: {e}")
        return False

    print("=" * 60)
    print("✓ All verification tests passed!")
    print("\nYou can now use JobFlow in your projects:")
    print("  from jobflow import RunScriptUseCase, ScriptConfig")
    return True


if __name__ == "__main__":
    success = verify_installation()
    sys.exit(0 if success else 1)

