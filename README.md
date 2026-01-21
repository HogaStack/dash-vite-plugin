# Dash Vite Plugin

A Dash plugin for integrating Vite using Dash 3.x hooks, allowing you to use modern frontend build tools with your Dash applications.

[![Tests](https://github.com/HogaStack/dash-vite-plugin/workflows/Tests/badge.svg)](https://github.com/HogaStack/dash-vite-plugin/actions)
[![Coverage](https://codecov.io/gh/HogaStack/dash-vite-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/HogaStack/dash-vite-plugin)
[![Python Version](https://img.shields.io/pypi/pyversions/dash-vite-plugin)](https://pypi.org/project/dash-vite-plugin/)
[![PyPI](https://img.shields.io/pypi/v/dash-vite-plugin)](https://pypi.org/project/dash-vite-plugin/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/pypi/l/dash-vite-plugin)](https://github.com/HogaStack/dash-vite-plugin/blob/main/LICENSE)

English | [简体中文](./README-zh_CN.md)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Example](#usage-example)
- [API Reference](#api-reference)
  - [VitePlugin Class](#viteplugin-class)
  - [NpmPackage Class](#npmpackage-class)
- [Configuration Options](#configuration-options)
- [How It Works](#how-it-works)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [License](#license)

## Introduction

Dash Vite Plugin is a plugin designed for the [Plotly Dash](https://plotly.com/dash/) framework that allows you to use the [Vite](https://vitejs.dev/) build tool in your Dash applications. The plugin leverages Dash 3.x's new hooks system to easily integrate modern frontend development tools into your Dash applications.

With this plugin, you can:

- Use Vue.js, React, or other frontend frameworks that support Vite
- Build optimized production versions
- Leverage modern frontend tooling with minimal configuration
- Integrate seamlessly with existing Dash applications
- Automatically build and integrate frontend assets with zero manual intervention

## Features

- ✅ Fully compatible with Dash 3.x
- ✅ Supports Vue.js and React
- ✅ Automated Node.js environment management
- ✅ Support for Less and Sass preprocessors
- ✅ Configurable build options
- ✅ Clean up build artifacts feature
- ✅ Intelligent skipping of recently built files for performance improvement
- ✅ Easy-to-use API

## Installation

```bash
pip install dash-vite-plugin
```

Note: This plugin requires Python 3.8 or higher.

## Quick Start

1. Install the plugin:

   ```bash
   pip install dash-vite-plugin
   ```

2. Prepare your frontend assets:

   ```console
   assets/
   ├── js/
   │   └── main.js
   └── vue/
       └── App.vue
   ```

3. Use the plugin in your Dash application:

   ```python
   from dash import Dash
   from dash_vite_plugin import VitePlugin
   
   # Create plugin instance
   vite_plugin = VitePlugin(
       build_assets_paths=['assets/js', 'assets/vue'],
       entry_js_paths=['assets/js/main.js'],
       npm_packages=[]
   )
   
   # Call setup() before creating Dash app
   vite_plugin.setup()
   
   # Create Dash app
   app = Dash(__name__)
   
   # Call use() after creating Dash app
   vite_plugin.use(app)
   ```

## Usage Example

For detailed usage examples, please refer to the example files:

- [React Basic Demo](./examples/react-basic-demo) - Basic usage with React
- [React Bits Grid Scan Demo](./examples/react-bits-grid-scan-demo) - Example: integrating `react-bits` GridScan component
- [React Bits Lightning Demo](./examples/react-bits-lightning-demo) - Example: integrating `react-bits` Lightning component
- [React Bits Shiny Text Demo](./examples/react-bits-shiny-text-demo) - Example: integrating `react-bits` ShinyText component
- [Vue Basic Demo](./examples/vue-basic-demo) - Basic usage with Vue

These examples show how to set up the plugin with different frontend frameworks and include test callbacks to verify that the integration is working correctly.

## API Reference

### VitePlugin Class

VitePlugin is the main plugin class responsible for managing the Vite build process.

#### VitePlugin Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| build_assets_paths | List[str] | Required | List of asset paths to build |
| entry_js_paths | List[str] | Required | List of entry JavaScript file paths |
| npm_packages | List[NpmPackage] | Required | List of npm packages |
| plugin_tmp_dir | str | '_vite' | Plugin temporary directory |
| support_less | bool | False | Whether to support Less |
| support_sass | bool | False | Whether to support Sass |
| download_node | bool | False | Whether to download Node.js if not found |
| node_version | str | '18.17.0' | Node.js version to download |
| clean_after | bool | False | Whether to clean up generated files after build |
| skip_build | bool | False | Whether to skip build execution |
| skip_build_if_recent | bool | True | Whether to skip build if built file was recently generated |
| skip_build_time_threshold | int | 5 | Time threshold in seconds to consider built file as recent |

#### VitePlugin Methods

##### setup()

Set up the Vite plugin, called before creating the Dash app.

```python
vite_plugin.setup()
```

##### use(app)

Use the plugin with a Dash app, called after creating the Dash app.

```python
vite_plugin.use(app)
```

Parameters:

- app (Dash): The Dash app instance to use

### NpmPackage Class

NpmPackage is used to define npm packages to install.

#### NpmPackage Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| name | str | Required | npm package name |
| version | str | 'latest' | npm package version |
| install_mode | Literal['-D', '-S'] | '-S' | Installation mode (-D for dev dependency, -S for prod dependency) |

#### NpmPackage Usage Example

```python
from dash_vite_plugin import NpmPackage

npm_packages = [
    NpmPackage('vue'),  # Use latest version
    NpmPackage('react', '18.2.0'),  # Specify version
    NpmPackage('sass', install_mode='-D'),  # Install as dev dependency
]
```

## Configuration Options

### Plugin Temporary Directory

The plugin creates a temporary directory during the build process to store build files. The default is `_vite`. You can customize it with the `plugin_tmp_dir` parameter:

```python
vite_plugin = VitePlugin(
    # ... other parameters
    plugin_tmp_dir='my_custom_dir'
)
```

### Less and Sass Support

To enable Less or Sass support, simply set the corresponding parameters to `True`:

```python
vite_plugin = VitePlugin(
    # ... other parameters
    support_less=True,  # Enable Less support
    support_sass=True,  # Enable Sass support
)
```

### Node.js Management

The plugin uses [py-node-manager](https://github.com/HogaStack/py-node-manager) to manage the Node.js environment:

```python
vite_plugin = VitePlugin(
    # ... other parameters
    download_node=True,      # Download Node.js if not found
    node_version='18.17.0'   # Specify Node.js version to download
)
```

### Cleanup Options

After building, you can choose to clean up generated files to keep the directory tidy:

```python
vite_plugin = VitePlugin(
    # ... other parameters
    clean_after=True  # Clean up files after build
)
```

### Build Skip Optimization

To avoid unnecessary repeated builds, the plugin can skip recently built files:

```python
vite_plugin = VitePlugin(
    # ... other parameters
    skip_build_if_recent=True,     # Enable build skipping
    skip_build_time_threshold=10   # Set time threshold to 10 seconds
)
```

## How It Works

1. **Initialization Phase**:
   - Plugin creates necessary config files (vite.config.js, index.html, package.json)
   - Copies specified asset files to temporary directory

2. **Installation Phase**:
   - Initializes npm environment
   - Installs Vite and related plugins
   - Installs specified npm packages
   - Installs Less or Sass support based on configuration

3. **Build Phase**:
   - Uses Vite to build assets
   - Generates optimized static files

4. **Integration Phase**:
   - Extracts built script and style tags
   - Injects them into Dash app's HTML
   - Sets up static file serving routes

5. **Cleanup Phase** (optional):
   - Deletes temporary files and directories to keep environment tidy

## Development Guide

### Project Structure

```console
dash-vite-plugin/
├── dash_vite_plugin/       # Plugin source code
│   ├── __init__.py         # Package initialization file
│   ├── plugin.py           # Main plugin class implementation
│   └── utils.py            # Utility functions and helper classes
├── tests/                  # Test files
│   ├── conftest.py         # Pytest configuration and fixtures
│   ├── test_plugin.py      # Tests for VitePlugin class functionality
│   ├── test_utils.py       # Tests for utility functions and ViteCommand class
│   └── test_dash_integration.py  # Integration tests with Dash application
├── example_vue.py          # Complete usage example demonstrating the plugin with Vue.js
├── example_react.py        # Complete usage example demonstrating the plugin with React
├── pyproject.toml          # Project configuration and metadata
├── requirements-dev.txt    # Development dependencies
└── ruff.toml               # Ruff linting configuration
```

### Development Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/HogaStack/dash-vite-plugin.git
   cd dash-vite-plugin
   ```

2. Install development dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install the project:

   ```bash
   pip install -e .
   ```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and code formatting. The configuration is in [ruff.toml](ruff.toml).

To check for linting issues:

```bash
ruff check .
```

To automatically fix linting issues:

```bash
ruff check . --fix
```

To check if the code conforms to the formatting standards without making changes:

```bash
ruff format . --check
```

To format the code according to the project's style guide:

```bash
ruff format .
```

### Running the Example

```bash
# Run the Vue.js example
python example_vue.py

# Run the React example
python example_react.py
```

## Testing

This project includes a comprehensive test suite covering unit tests and integration tests.

### Test Structure

- `conftest.py`: Contains pytest configuration and fixtures
- `test_plugin.py`: Tests main functionality of VitePlugin class
- `test_utils.py`: Tests utility functions and ViteCommand class
- `test_dash_integration.py`: Integration tests for VitePlugin with Dash app integration

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_plugin.py -v

# Run integration tests
python -m pytest tests/test_dash_integration.py -v
```

### Test Dependencies

Make sure you have installed the test dependencies:

```bash
pip install -r requirements-dev.txt
```

This will install:

- py-node-manager: For managing Node.js environment
- pytest: Testing framework
- pytest-cov: Coverage reporting for tests
- dash[testing]: Dash framework testing dependencies

### Test Coverage

Tests cover the following functionalities:

1. Initialization and configuration of VitePlugin class
2. Functionality of utility functions and ViteCommand class
3. File copying and asset handling
4. Integration tests with different configuration options
5. Mock tests to avoid actual Node.js calls

## License

See [LICENSE](LICENSE) file for details.
