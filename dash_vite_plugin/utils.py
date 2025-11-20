import logging
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from py_node_manager import get_logger, NodeManager
from typing import List, Literal
from typing_extensions import Self


logger = get_logger(logging.getLogger(__name__))


@dataclass
class NpmPackage:
    """
    NpmPackage TypedDict
    """

    name: str
    version: str = 'latest'
    install_mode: Literal['-D', '-S'] = '-S'


class ViteCommand:
    """
    ViteCommand class
    """

    def __init__(
        self,
        entry_js_paths: List[str],
        npm_packages: List[NpmPackage],
        plugin_tmp_dir: str,
        support_less: bool,
        support_sass: bool,
        download_node: bool,
        node_version: str,
        is_cli: bool,
    ):
        """
        Initialize the ViteCommand class

        Args:
            entry_js_paths (List[str]): A list of entry JavaScript file paths
            npm_packages (List[NpmPackage]): A list of npm packages
            plugin_tmp_dir (str): Temporary directory for plugin files
            support_less (bool): Whether to support Less
            support_sass (bool): Whether to support Sass
            download_node (bool): Whether to download Node.js if not found
            node_version (str): Node.js version to download if download_node is True
            is_cli (bool): Whether the command is being run from the CLI
        """
        node_manager = NodeManager(download_node=download_node, node_version=node_version, is_cli=False)
        self.node_path = node_manager.node_path
        self.node_env = node_manager.node_env
        self.npm_path = node_manager.npm_path
        self.npx_path = node_manager.npx_path
        self.entry_js_paths = entry_js_paths
        self.npm_packages = npm_packages
        self.support_less = support_less
        self.support_sass = support_sass
        self.is_cli = is_cli
        # Ensure the plugin_tmp_dir directory exists
        self.plugin_tmp_dir = plugin_tmp_dir
        if not os.path.exists(self.plugin_tmp_dir):
            os.makedirs(self.plugin_tmp_dir)
        self.index_html_path = f'{self.plugin_tmp_dir}/index.html'
        self.config_js_path = f'{self.plugin_tmp_dir}/vite.config.js'
        self.package_json_path = f'{self.plugin_tmp_dir}/package.json'

    def create_default_vite_config(self) -> None:
        """
        Create a default Vite config file

        Returns:
            None
        """

        config_content = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command }) => {
  return {
    plugins: [react(), vue()],
    resolve: {
      // https://cn.vitejs.dev/config/#resolve-alias
      alias: {
        // Set path
        '~': path.resolve(__dirname, './'),
        // Set alias
        '@': path.resolve(__dirname, './src')
      },
      // https://cn.vitejs.dev/config/#resolve-extensions
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
    },
    // Build configuration
    build: {
      // https://vite.dev/config/build-options.html
      sourcemap: command === 'build' ? false : 'inline',
      outDir: 'dist',
      assetsDir: 'assets',
      chunkSizeWarningLimit: 2000,
      rollupOptions: {
        output: {
          chunkFileNames: '_static/js/[name]-[hash].js',
          entryFileNames: '_static/js/[name]-[hash].js',
          assetFileNames: '_static/[ext]/[name]-[hash].[ext]'
        }
      }
    },
  }
})"""

        with open(self.config_js_path, 'w') as f:
            f.write(config_content)

    def create_default_index_html(self) -> None:
        """
        Create a default index.html file

        Returns:
            None
        """
        script_content = '\n    '.join(
            [f'<script type="module" src="{entry_js_path}"></script>' for entry_js_path in self.entry_js_paths]
        )
        index_html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="renderer" content="webkit">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
  </head>
  <body>
    {script_content}
  </body>
</html>"""

        with open(self.index_html_path, 'w') as f:
            f.write(index_html_content)

    def _check_npm_init(self) -> bool:
        """
        Check if npm init has been run

        Returns:
            bool: True if npm init has been run, False otherwise
        """
        return os.path.exists(self.package_json_path)

    def _check_vite(self) -> bool:
        """
        Check if Vite is installed

        Returns:
            bool: True if Vite is installed, False otherwise
        """
        check_cmd = [self.npx_path, 'vite --help']

        result = subprocess.run(check_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env)
        return result.returncode == 0

    def _check_npm_package(self, package_name: str, package_type: Literal['devDependencies', 'dependencies']) -> bool:
        """
        Check if a specific npm package is installed by checking package.json

        Args:
            package_name (str): The name of the npm package
            package_type (Literal['devDependencies', 'dependencies']): The type of dependency to check

        Returns:
            bool: True if the package is installed, False otherwise
        """
        if not os.path.exists(self.package_json_path):
            return False

        try:
            with open(self.package_json_path, 'r') as f:
                package_json = json.load(f)
                dependencies = package_json.get(package_type, {})
                return package_name in dependencies
        except Exception:
            return False

    def _check_less(self) -> bool:
        """
        Check if Less is installed by checking package.json devDependencies

        Returns:
            bool: True if Less is installed, False otherwise
        """
        return self._check_npm_package('less', 'devDependencies')

    def _check_sass(self) -> bool:
        """
        Check if Sass is installed by checking package.json devDependencies

        Returns:
            bool: True if Sass is installed, False otherwise
        """
        return self._check_npm_package('sass', 'devDependencies')

    def _install_vite(self) -> None:
        """
        Install Vite

        Returns:
            None
        """
        logger.info('📥 Start installing Vite...')
        try:
            if not self._check_vite():
                install_cmd = [
                    self.npm_path,
                    'install',
                    '-D',
                    'vite',
                    '@vitejs/plugin-react',
                    '@vitejs/plugin-vue',
                ]
                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Vite installed successfully!')

        except Exception as e:
            logger.error(f'❌ Error installing Vite: {e}')
            raise e

    def _install_less(self) -> None:
        """
        Install Less

        Returns:
            None
        """
        logger.info('📥 Start installing Less...')
        try:
            if not self._check_less():
                install_cmd = [
                    self.npm_path,
                    'install',
                    '-D',
                    'less',
                ]
                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Less installed successfully!')

        except Exception as e:
            logger.error(f'❌ Error installing Less: {e}')
            raise e

    def _install_sass(self) -> None:
        """
        Install Sass

        Returns:
            None
        """
        logger.info('📥 Start installing Sass...')
        try:
            if not self._check_sass():
                install_cmd = [
                    self.npm_path,
                    'install',
                    '-D',
                    'sass',
                ]
                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Sass installed successfully!')

        except Exception as e:
            logger.error(f'❌ Error installing Sass: {e}')
            raise e

    def _install_npm_packages(self) -> None:
        """
        Install npm packages

        Returns:
            None
        """
        logger.info('📥 Start installing npm packages...')
        try:
            for package in self.npm_packages:
                install_cmd = [
                    self.npm_path,
                    'install',
                    package.install_mode,
                    f'{package.name}@{package.version}',
                ]
                result = subprocess.run(
                    install_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ npm packages installed successfully!')

        except Exception as e:
            logger.error(f'❌ Error installing npm packages: {e}')
            raise e

    def init(self) -> Self:
        """
        Initialize Vite

        Returns:
            Self: The ViteCommand instance
        """
        logger.info('🚀 Start initializing Vite...')
        try:
            # Create default config if it doesn't exist
            if self.is_cli:
                logger.info('⚙️ Creating Vite config file...')

            if not os.path.exists(self.config_js_path):
                if self.is_cli:
                    logger.info(f'🔍 Config file {self.config_js_path} not found. Creating default config file...')

                self.create_default_vite_config()

                if self.is_cli:
                    logger.info(f'💾 Default config file created at: {self.config_js_path}')

            if self.is_cli:
                logger.info('⚙️ Creating index.html file...')

            self.create_default_index_html()

            if self.is_cli:
                logger.info(f'💾 Default index.html file created at: {self.index_html_path}')

            if not self._check_npm_init():
                init_cmd = [self.npm_path, 'init', '-y']
                result = subprocess.run(
                    init_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)

            logger.info('✅ Vite initialized successfully!')

        except Exception as e:
            logger.error(f'❌ Error initializing Vite: {e}')
            raise e

        return self

    def install(self) -> Self:
        """
        Install Vite and npm packages

        Returns:
            Self: The ViteCommand instance
        """
        self._install_vite()
        if self.support_less:
            self._install_less()
        if self.support_sass:
            self._install_sass()
        self._install_npm_packages()

        return self

    def build(self) -> Self:
        """
        Build assets using Vite

        Returns:
            Self: The ViteCommand instance
        """
        logger.info('🔨 Building assets using Vite...')
        try:
            build_cmd: List[str] = [self.npx_path, 'vite', 'build']

            result = subprocess.run(
                build_cmd, capture_output=True, text=True, cwd=self.plugin_tmp_dir, env=self.node_env
            )

            if result.returncode != 0:
                raise RuntimeError(result.stderr)

            logger.info('✅ Build completed successfully!')

        except Exception as e:
            logger.error(f'❌ Error building assets using Vite: {e}')
            raise e

        return self

    def clean(self, extra_clean_files: List[str], extra_clean_dirs: List[str]) -> Self:
        """
        Clean up generated files to keep directory clean

        Args:
            extra_clean_files: List[str]: List of extra files to clean
            extra_clean_dirs: List[str]: List of extra directories to clean

        Returns:
            Self: The ViteCommand instance
        """
        logger.info('🧹 Cleaning up generated files...')
        try:
            files_to_remove = [
                self.config_js_path,
                self.index_html_path,
                self.package_json_path,
                f'{self.plugin_tmp_dir}/package-lock.json',
            ]
            files_to_remove.extend(extra_clean_files)

            directories_to_remove = [f'{self.plugin_tmp_dir}/node_modules']
            directories_to_remove.extend(extra_clean_dirs)

            # Remove files
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        if self.is_cli:
                            logger.info(f'🗑️ Removed {file_path}')
                    except Exception as e:
                        logger.warning(f'⚠️ Warning: Could not remove {file_path}: {e}')

            # Remove directories
            for dir_path in directories_to_remove:
                if os.path.exists(dir_path):
                    try:
                        shutil.rmtree(dir_path)
                        if self.is_cli:
                            logger.info(f'🗑️ Removed {dir_path}')
                    except Exception as e:
                        logger.warning(f'⚠️ Warning: Could not remove {dir_path}: {e}')

            logger.info('✅ Cleanup completed.')

        except Exception as e:
            logger.error(f'❌ Error cleaning up: {e}')
            raise e

        return self
