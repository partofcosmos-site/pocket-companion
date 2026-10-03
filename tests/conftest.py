"""Pytest configuration ensuring mock CircuitPython hardware modules are present."""

import sys
import pytest
from tests.mock_hardware import install_mock_modules, uninstall_mock_modules

# Eagerly install mocks into sys.modules so `import code` succeeds everywhere
install_mock_modules()


@pytest.fixture(autouse=True, scope="function")
def ensure_mock_hardware():
    """Ensure mock modules are clean and available for every test."""
    install_mock_modules()
    yield
