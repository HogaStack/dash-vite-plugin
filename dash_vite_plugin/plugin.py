import logging
import os
import re
import shutil
import time
from dash import Dash, hooks
from flask import send_from_directory
from py_node_manager import get_logger
from typing import List
from .utils import NpmPackage, ViteCommand


logger = get_logger(logging.getLogger(__name__))


class VitePlugin:
    """
    A plugin for using Vite with Dash
    """

    def __init__(
        self,
        build_assets_paths: List[str],
        entry_js_paths: List[str],
        npm_packages: List[NpmPackage],
        plugin_tmp_dir: str = '_vite',
        support_less: bool = False,
        support_sass: bool = False,
        download_node: bool = False,
        node_version: str = '18.20.8',
        clean_after: bool = False,
        skip_build: bool = False,
        skip_build_if_recent: bool = True,
        skip_build_time_threshold: int = 5,
    ) -> None:
        """
        Initialize the Vite plugin

        Args:
            build_assets_paths (List[str]): A list of build asset paths
            entry_js_paths (List[str]): A list of entry JavaScript file paths
            npm_packages (List[NpmPackage]): A list of npm packages
            plugin_tmp_dir (str): Temporary directory for plugin files
            support_less (bool): Whether to support Less
            support_sass (bool): Whether to support Sass
            download_node (bool): Whether to download Node.js if not found
            node_version (str): Node.js version to download if download_node is True
            clean_after (bool): Whether to clean up generated files after build
            skip_build (bool): Whether to skip build execution
            skip_build_if_recent (bool): Whether to skip build if built file was recently generated
            skip_build_time_threshold (int): Time threshold in seconds to consider built file as recent
        """
        self.build_assets_paths = build_assets_paths
        self.entry_js_paths = entry_js_paths
        self.npm_packages = npm_packages
        self.plugin_tmp_dir = plugin_tmp_dir
        self.support_less = support_less
        self.support_sass = support_sass
        self.download_node = download_node
        self.node_version = node_version
        self.clean_after = clean_after
        self.skip_build = skip_build
        self.skip_build_if_recent = skip_build_if_recent
        self.skip_build_time_threshold = skip_build_time_threshold
        self.vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=support_less,
            support_sass=support_sass,
            download_node=download_node,
            node_version=node_version,
            is_cli=False,
        )
        self._clean_files = []
        self._clean_dirs = []

    def _copy_build_assets(self) -> None:
        """
        Copy files and directories from build_assets_paths to plugin_tmp_dir
        """
        # Ensure the plugin_tmp_dir exists
        if not os.path.exists(self.plugin_tmp_dir):
            os.makedirs(self.plugin_tmp_dir)

        # Copy each item in build_assets_paths to plugin_tmp_dir
        for asset_path in self.build_assets_paths:
            if os.path.exists(asset_path):
                # Preserve directory structure by using relative path
                if asset_path.startswith('./'):
                    # Remove './' prefix
                    relative_path = asset_path[2:]
                else:
                    relative_path = asset_path

                dest_path = os.path.join(self.plugin_tmp_dir, relative_path)

                # Ensure parent directory exists
                dest_dir = os.path.dirname(dest_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                # Remove destination if it already exists
                if os.path.exists(dest_path):
                    if os.path.isfile(dest_path):
                        os.remove(dest_path)
                    else:
                        shutil.rmtree(dest_path)

                # Copy file or directory
                if os.path.isfile(asset_path):
                    self._clean_files.append(f'{self.plugin_tmp_dir}/{relative_path}')
                    shutil.copy2(asset_path, dest_path)
                else:
                    # Extract the root directory name from the relative path
                    root_dir = relative_path.split('/')[0] if '/' in relative_path else relative_path
                    self._clean_dirs.append(f'{self.plugin_tmp_dir}/{root_dir}')
                    shutil.copytree(asset_path, dest_path)
            else:
                raise FileNotFoundError(f"Asset path '{asset_path}' does not exist.")

    def _build_assets_with_vite(self) -> None:
        """
        Build assets using Vite

        Returns:
            None
        """
        built = self.vite_command.init().install().build()
        if self.clean_after:
            built.clean(self._clean_files, self._clean_dirs)

    def _extract_assets_tags(self) -> str:
        """
        Extract script and link tags from dist/index.html

        Returns:
            str: Combined script and link tags
        """
        tags_to_insert = ''

        # Extract script and link tags from dist/index.html
        dist_index_path = os.path.join(self.plugin_tmp_dir, 'dist', 'index.html')
        if os.path.exists(dist_index_path):
            with open(dist_index_path, 'r', encoding='utf-8') as f:
                dist_index_content = f.read()

            # Extract all script and link tags
            script_tags = re.findall(r'<script[^>]*>.*?</script>', dist_index_content, re.DOTALL)
            link_tags = re.findall(r'<link[^>]*>', dist_index_content)

            # Combine all tags
            tags_to_insert = '\n'.join(link_tags + script_tags)

        return tags_to_insert

    def _set_assets_path_ignore(self, app: Dash) -> None:
        """
        Extract paths starting with 'assets' or './assets' from build_assets_paths
        and set them as assets_path_ignore for the Dash app

        Args:
            app (Dash): The Dash app to configure

        Returns:
            None
        """
        # Get the assets folder from app config
        assets_folder = app.config.assets_folder

        # Extract the directory name from the assets folder path
        assets_dir_name = os.path.basename(assets_folder)

        # Extract paths starting with assets_dir_name or './' + assets_dir_name and remove prefix
        assets_to_ignore = []
        prefix1 = f'{assets_dir_name}/'
        prefix2 = f'./{assets_dir_name}/'

        for path in self.build_assets_paths:
            if path.startswith(prefix1):
                # Remove prefix1 prefix
                assets_to_ignore.append(path[len(prefix1) :])
            elif path.startswith(prefix2):
                # Remove prefix2 prefix
                assets_to_ignore.append(path[len(prefix2) :])

        # Set assets_path_ignore if any paths were found
        if assets_to_ignore:
            if not app.config.assets_path_ignore:
                app.config.assets_path_ignore = []
            app.config.assets_path_ignore.extend(assets_to_ignore)

    def _should_skip_build(self) -> bool:
        """
        Check if the build should be skipped based on the skip_build_if_recent setting

        Returns:
            bool: True if the build should be skipped, False otherwise
        """
        if self.skip_build:
            return True
        # Check if CSS file exists and was generated recently (within threshold seconds)
        check_index_path = os.path.join(self.plugin_tmp_dir, 'dist', 'index.html')
        if self.skip_build_if_recent and os.path.exists(check_index_path):
            file_mod_time = os.path.getmtime(check_index_path)
            current_time = time.time()
            if current_time - file_mod_time < self.skip_build_time_threshold:
                logger.info(
                    f'⚡ Built assets file was generated recently '
                    f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                )
                return True
        return False

    def setup(self) -> None:
        """
        Setup the Vite plugin

        Returns:
            None
        """

        @hooks.setup(priority=2)
        def build_assets(app: Dash):
            # Use the new method to check if we should skip the build
            if self._should_skip_build():
                return
            self._copy_build_assets()
            self._build_assets_with_vite()

        @hooks.index(priority=1)
        def add_built_assets(index_string: str) -> str:
            # Extract script and link tags from dist/index.html
            tags_to_insert = self._extract_assets_tags()

            # Insert tags into head section
            if tags_to_insert:
                replacement = f'{tags_to_insert}\n\\1'
                index_string = re.sub(r'(</head>)', replacement, index_string, count=1)

            return index_string

    def use(self, app: Dash) -> None:
        """
        Use the Vite plugin with a Dash app

        Args:
            app (Dash): The Dash app to use the plugin with

        Returns:
            None
        """
        # Set assets_path_ignore for the Dash app
        self._set_assets_path_ignore(app)

        # Use absolute path for plugin_tmp_dir to avoid path resolution issues
        plugin_tmp_dir_abs = os.path.abspath(self.plugin_tmp_dir)

        # Add route to serve static files generated by Vite
        @app.server.route('/_static/<path:file_path>')
        def serve_static(file_path):
            return send_from_directory(plugin_tmp_dir_abs, f'dist/_static/{file_path}')
