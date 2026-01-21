# Dash Vite Plugin

一个用于在 Dash 应用中集成 Vite 的插件，利用 Dash 3.x hooks机制，让您能够在 Dash 应用中使用现代化的前端构建工具。

[![Tests](https://github.com/HogaStack/dash-vite-plugin/workflows/Tests/badge.svg)](https://github.com/HogaStack/dash-vite-plugin/actions)
[![Coverage](https://codecov.io/gh/HogaStack/dash-vite-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/HogaStack/dash-vite-plugin)
[![Python Version](https://img.shields.io/pypi/pyversions/dash-vite-plugin)](https://pypi.org/project/dash-vite-plugin/)
[![PyPI](https://img.shields.io/pypi/v/dash-vite-plugin)](https://pypi.org/project/dash-vite-plugin/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/pypi/l/dash-vite-plugin)](https://github.com/HogaStack/dash-vite-plugin/blob/main/LICENSE)

[English](./README.md) | 简体中文

## 目录

- [简介](#简介)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [API 参考](#api-参考)
  - [VitePlugin 类](#viteplugin-类)
  - [NpmPackage 类](#npmpackage-类)
- [配置选项](#配置选项)
- [工作原理](#工作原理)
- [开发指南](#开发指南)
- [测试](#测试)
- [许可证](#许可证)

## 简介

Dash Vite Plugin 是为 [Plotly Dash](https://plotly.com/dash/) 框架设计的插件，允许您在 Dash 应用中使用 [Vite](https://vitejs.dev/) 构建工具。该插件利用 Dash 3.x 的新hooks机制，轻松将现代前端开发工具集成到您的 Dash 应用中。

通过此插件，您可以：

- 使用支持 Vite 的 Vue.js、React 或其他前端框架
- 构建优化的生产版本
- 利用现代前端工具，配置最少
- 与现有 Dash 应用无缝集成
- 自动构建和集成前端资源，无需手动干预

## 特性

- ✅ 完全兼容 Dash 3.x
- ✅ 支持 Vue.js 和 React
- ✅ 自动化 Node.js 环境管理
- ✅ 支持 Less 和 Sass 预处理器
- ✅ 可配置的构建选项
- ✅ 清理构建产物功能
- ✅ 智能跳过最近构建的文件以提高性能
- ✅ 易于使用的 API

## 安装

```bash
pip install dash-vite-plugin
```

注意：此插件需要 Python 3.8 或更高版本。

## 快速开始

1. 安装插件：

   ```bash
   pip install dash-vite-plugin
   ```

2. 准备您的前端资源：

   ```console
   assets/
   ├── js/
   │   └── main.js
   └── vue/
       └── App.vue
   ```

3. 在您的 Dash 应用中使用插件：

   ```python
   from dash import Dash
   from dash_vite_plugin import VitePlugin
   
   # 创建插件实例
   vite_plugin = VitePlugin(
       build_assets_paths=['assets/js', 'assets/vue'],
       entry_js_paths=['assets/js/main.js'],
       npm_packages=[]
   )
   
   # 在创建 Dash 应用前调用 setup()
   vite_plugin.setup()
   
   # 创建 Dash 应用
   app = Dash(__name__)
   
   # 在创建 Dash 应用后调用 use()
   vite_plugin.use(app)
   ```

## 使用示例

有关详细的使用示例，请参阅示例文件：

- [React Basic Demo](./examples/react-basic-demo) - 集成`React`的基础示例
- [React Bits Grid Scan Demo](./examples/react-bits-grid-scan-demo) - 示例：集成使用`react-bits`中的`GridScan`组件
- [React Bits Lightning Demo](./examples/react-bits-lightning-demo) - 示例：集成使用`react-bits`中的`Lightning`组件
- [React Bits Shiny Text Demo](./examples/react-bits-shiny-text-demo) - 示例：集成使用`react-bits`中的`ShinyText`组件
- [Vue Basic Demo](./examples/vue-basic-demo) - 集成`Vue`的基础示例


这些示例展示了如何使用不同前端框架设置插件，并包含测试回调以验证集成是否正常工作。

## API 参考

### VitePlugin 类

VitePlugin 是负责管理 Vite 构建过程的主要插件类。

#### VitePlugin 构造函数参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| build_assets_paths | List[str] | 必需 | 要构建的资源路径列表 |
| entry_js_paths | List[str] | 必需 | 入口 JavaScript 文件路径列表 |
| npm_packages | List[NpmPackage] | 必需 | npm 包列表 |
| plugin_tmp_dir | str | '_vite' | 插件临时目录 |
| support_less | bool | False | 是否支持 Less |
| support_sass | bool | False | 是否支持 Sass |
| download_node | bool | False | 如果未找到是否下载 Node.js |
| node_version | str | '18.17.0' | 要下载的 Node.js 版本 |
| clean_after | bool | False | 构建后是否清理生成的文件 |
| skip_build | bool | False | 是否跳过构建执行 |
| skip_build_if_recent | bool | True | 如果构建文件是最近生成的是否跳过构建 |
| skip_build_time_threshold | int | 5 | 考虑构建文件为最近的时间阈值（秒）|

#### VitePlugin 方法

##### setup()

设置 Vite 插件，在创建 Dash 应用之前调用。

```python
vite_plugin.setup()
```

##### use(app)

将插件与 Dash 应用一起使用，在创建 Dash 应用之后调用。

```python
vite_plugin.use(app)
```

参数：

- app (Dash): 要使用的 Dash 应用实例

### NpmPackage 类

NpmPackage 用于定义要安装的 npm 包。

#### NpmPackage 构造函数参数

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| name | str | 必需 | npm 包名称 |
| version | str | 'latest' | npm 包版本 |
| install_mode | Literal['-D', '-S'] | '-S' | 安装模式 (-D 表示开发依赖, -S 表示生产依赖) |

#### NpmPackage 使用示例

```python
from dash_vite_plugin import NpmPackage

npm_packages = [
    NpmPackage('vue'),  # 使用最新版本
    NpmPackage('react', '18.2.0'),  # 指定版本
    NpmPackage('sass', install_mode='-D'),  # 作为开发依赖安装
]
```

## 配置选项

### 插件临时目录

插件在构建过程中会创建一个临时目录来存储构建文件。默认是 `_vite`。您可以使用 `plugin_tmp_dir` 参数自定义它：

```python
vite_plugin = VitePlugin(
    # ... 其他参数
    plugin_tmp_dir='my_custom_dir'
)
```

### Less 和 Sass 支持

要启用 Less 或 Sass 支持，只需将相应参数设置为 `True`：

```python
vite_plugin = VitePlugin(
    # ... 其他参数
    support_less=True,  # 启用 Less 支持
    support_sass=True,  # 启用 Sass 支持
)
```

### Node.js 管理

插件使用 [py-node-manager](https://github.com/HogaStack/py-node-manager) 来管理 Node.js 环境：

```python
vite_plugin = VitePlugin(
    # ... 其他参数
    download_node=True,      # 如果未找到则下载 Node.js
    node_version='18.17.0'   # 指定要下载的 Node.js 版本
)
```

### 清理选项

构建后，您可以选择清理生成的文件以保持目录整洁：

```python
vite_plugin = VitePlugin(
    # ... 其他参数
    clean_after=True  # 构建后清理文件
)
```

### 构建跳过优化

为了避免不必要的重复构建，插件可以跳过最近构建的文件：

```python
vite_plugin = VitePlugin(
    # ... 其他参数
    skip_build_if_recent=True,     # 启用构建跳过
    skip_build_time_threshold=10   # 设置时间阈值为 10 秒
)
```

## 工作原理

1. **初始化阶段**：
   - 插件创建必要的配置文件（vite.config.js、index.html、package.json）
   - 将指定的资源文件复制到临时目录

2. **安装阶段**：
   - 初始化 npm 环境
   - 安装 Vite 和相关插件
   - 安装指定的 npm 包
   - 根据配置安装 Less 或 Sass 支持

3. **构建阶段**：
   - 使用 Vite 构建资源
   - 生成优化的静态文件

4. **集成阶段**：
   - 提取构建的脚本和样式标签
   - 将它们注入到 Dash 应用的 HTML 中
   - 设置静态文件服务路由

5. **清理阶段**（可选）：
   - 删除临时文件和目录以保持环境整洁

## 开发指南

### 项目结构

```console
dash-vite-plugin/
├── dash_vite_plugin/       # 插件源代码
│   ├── __init__.py         # 包初始化文件
│   ├── plugin.py           # 主插件类实现
│   └── utils.py            # 工具函数和辅助类
├── tests/                  # 测试文件
│   ├── conftest.py         # Pytest 配置和夹具
│   ├── test_plugin.py      # VitePlugin 类功能测试
│   ├── test_utils.py       # 工具函数和 ViteCommand 类测试
│   └── test_dash_integration.py  # 与 Dash 应用集成的集成测试
├── example_vue.py          # 完整的使用示例演示插件（Vue.js版本）
├── example_react.py        # 完整的使用示例演示插件（React版本）
├── pyproject.toml          # 项目配置和元数据
├── requirements-dev.txt    # 开发依赖
└── ruff.toml               # Ruff 代码检查配置
```

### 开发环境设置

1. 克隆仓库：

   ```bash
   git clone https://github.com/HogaStack/dash-vite-plugin.git
   cd dash-vite-plugin
   ```

2. 安装开发依赖：

   ```bash
   pip install -r requirements-dev.txt
   ```

3. 安装项目：

   ```bash
   pip install -e .
   ```

### 代码质量

本项目使用 [Ruff](https://github.com/astral-sh/ruff) 进行代码检查和格式化。配置在 [ruff.toml](ruff.toml) 中。

检查代码检查问题：

```bash
ruff check .
```

自动修复代码检查问题：

```bash
ruff check . --fix
```

检查代码是否符合格式标准而不进行更改：

```bash
ruff format . --check
```

根据项目的风格指南格式化代码：

```bash
ruff format .
```

### 运行示例

```bash
# 运行 Vue.js 示例
python example_vue.py

# 运行 React 示例
python example_react.py
```

## 测试

本项目包含涵盖单元测试和集成测试的综合测试套件。

### 测试结构

- `conftest.py`：包含 pytest 配置和夹具
- `test_plugin.py`：测试 VitePlugin 类的主要功能
- `test_utils.py`：测试工具函数和 ViteCommand 类
- `test_dash_integration.py`：测试 VitePlugin 与 Dash 应用的集成

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_plugin.py -v

# 运行集成测试
python -m pytest tests/test_dash_integration.py -v
```

### 测试依赖

确保您已安装测试依赖：

```bash
pip install -r requirements-dev.txt
```

这将安装：

- py-node-manager：用于管理 Node.js 环境
- pytest：测试框架
- pytest-cov：测试覆盖率报告
- dash[testing]：Dash 框架测试依赖

### 测试覆盖

测试涵盖以下功能：

1. VitePlugin 类的初始化和配置
2. 工具函数和 ViteCommand 类的功能
3. 文件复制和资源处理
4. 不同配置选项的集成测试
5. 避免实际 Node.js 调用的模拟测试

## 许可证

详见 [LICENSE](LICENSE) 文件。
