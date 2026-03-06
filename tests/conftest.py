import os
import pytest
import sys
import shutil
import tempfile
from selenium.webdriver.chrome.options import Options


# Add the project root to the Python path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def test_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_working_directory():
    """Create a temporary working directory for tests."""
    original_cwd = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir, ignore_errors=True)


def pytest_setup_options():
    options = Options()
    chrome_binary = os.environ.get('CHROME_BINARY')
    if chrome_binary:
        options.binary_location = chrome_binary
    return options
