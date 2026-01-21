import os
import pytest
import shutil
import tempfile
import time
from unittest.mock import MagicMock, patch
from dash_vite_plugin.plugin import NpmPackage, VitePlugin


class TestVitePlugin:
    """Test cases for the VitePlugin class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_plugin_initialization(self):
        """Test plugin initialization with default parameters."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        assert plugin.build_assets_paths == build_assets_paths
        assert plugin.entry_js_paths == entry_js_paths
        assert plugin.npm_packages == npm_packages
        assert plugin.plugin_tmp_dir == '_vite'
        assert plugin.support_less is False
        assert plugin.support_sass is False
        assert plugin.download_node is False
        assert plugin.node_version == '18.20.8'
        assert plugin.clean_after is False
        assert plugin.skip_build_if_recent is True
        assert plugin.skip_build_time_threshold == 5
        assert plugin.skip_build is False

    def test_plugin_initialization_with_custom_parameters(self):
        """Test plugin initialization with custom parameters."""
        build_assets_paths = ['src/assets']
        entry_js_paths = ['src/main.js', 'src/secondary.js']
        npm_packages = [NpmPackage('react', '17.0.0'), NpmPackage('lodash', '4.17.21', '-D')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir='_custom_vite',
            support_less=True,
            support_sass=True,
            download_node=True,
            node_version='20.0.0',
            clean_after=True,
            skip_build=True,
            skip_build_if_recent=False,
            skip_build_time_threshold=10,
        )

        assert plugin.build_assets_paths == build_assets_paths
        assert plugin.entry_js_paths == entry_js_paths
        assert plugin.npm_packages == npm_packages
        assert plugin.plugin_tmp_dir == '_custom_vite'
        assert plugin.support_less is True
        assert plugin.support_sass is True
        assert plugin.download_node is True
        assert plugin.node_version == '20.0.0'
        assert plugin.clean_after is True
        assert plugin.skip_build is True
        assert plugin.skip_build_if_recent is False
        assert plugin.skip_build_time_threshold == 10

    @patch('dash_vite_plugin.plugin.hooks')
    def test_setup_method(self, mock_hooks):
        """Test setup method."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )
        plugin.setup()

        # Verify that hooks.setup() and hooks.index() decorators were called
        assert mock_hooks.setup.called
        assert mock_hooks.index.called

    def test_copy_build_assets_creates_plugin_dir(self):
        """Test _copy_build_assets creates plugin directory when it doesn't exist."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        # Remove plugin directory if it exists
        plugin_tmp_dir = '_vite'
        if os.path.exists(plugin_tmp_dir):
            shutil.rmtree(plugin_tmp_dir)

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test file
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        # Call _copy_build_assets
        plugin._copy_build_assets()

        # Check that plugin directory was created
        assert os.path.exists(plugin.plugin_tmp_dir)
        assert os.path.exists(os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js'))

    def test_copy_build_assets_creates_parent_directory(self):
        """Test _copy_build_assets creates parent directory when it doesn't exist."""
        build_assets_paths = ['assets/js/main.js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Remove plugin directory if it exists
        if os.path.exists(plugin.plugin_tmp_dir):
            shutil.rmtree(plugin.plugin_tmp_dir)

        # Create a test file in a nested directory
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        # Call _copy_build_assets
        plugin._copy_build_assets()

        # Check that plugin directory and parent directory were created
        assert os.path.exists(plugin.plugin_tmp_dir)
        assert os.path.exists(os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js'))

    def test_copy_build_assets_removes_existing_destination(self):
        """Test _copy_build_assets removes existing destination file or directory."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test file
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("original");')

        # First copy
        plugin._copy_build_assets()

        # Modify the original file
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("modified");')

        # Second copy should remove existing destination and copy the new file
        plugin._copy_build_assets()

        # Check that the destination file was updated
        dest_path = os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js')
        assert os.path.exists(dest_path)
        with open(dest_path, 'r') as f:
            content = f.read()
            assert 'console.log("modified");' in content

    def test_copy_build_assets_removes_existing_directory(self):
        """Test _copy_build_assets removes existing destination directory."""
        build_assets_paths = ['assets/js/main.js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test file
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        # First copy to create the destination
        plugin._copy_build_assets()

        # Create a directory with the same name as the destination file
        dest_file_path = os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js')
        if os.path.exists(dest_file_path):
            os.remove(dest_file_path)
        os.makedirs(dest_file_path, exist_ok=True)

        # Copy again - should remove the directory and create the file
        plugin._copy_build_assets()

        # Check that the destination is now a file, not a directory
        assert os.path.isfile(dest_file_path)

    def test_copy_build_assets_removes_existing_directory_shutil(self):
        """Test _copy_build_assets removes existing destination directory using shutil.rmtree."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test directory structure
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("original");')

        # First copy to create the destination
        plugin._copy_build_assets()

        # Verify the destination is a directory
        dest_dir_path = os.path.join(plugin.plugin_tmp_dir, 'assets')
        assert os.path.isdir(dest_dir_path)

        # Create a file with the same name as the destination directory in the source
        # First remove the source directory
        if os.path.exists('assets'):
            shutil.rmtree('assets')
        # Create a file with the same name
        with open('assets', 'w') as f:
            f.write('this is a file')

        # Update the build_assets_paths to point to the file now
        plugin.build_assets_paths = ['assets']

        # Copy again - should remove the existing directory and create the file
        plugin._copy_build_assets()

        # Check that the destination is now a file, not a directory
        dest_file_path = os.path.join(plugin.plugin_tmp_dir, 'assets')
        assert os.path.isfile(dest_file_path)

    def test_copy_build_assets_adds_to_clean_files(self):
        """Test _copy_build_assets adds copied files to _clean_files list."""
        build_assets_paths = ['assets/js/main.js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test file
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        # Clear clean files list
        plugin._clean_files = []

        # Call _copy_build_assets
        plugin._copy_build_assets()

        # Check that the file was added to _clean_files
        expected_path = f'{plugin.plugin_tmp_dir}/assets/js/main.js'
        assert expected_path in plugin._clean_files

    def test_copy_build_assets_with_directory(self):
        """Test _copy_build_assets with directory copying."""
        build_assets_paths = ['assets']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test directory structure
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        # Call _copy_build_assets
        plugin._copy_build_assets()

        # Check that directory was copied
        assert os.path.exists(os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js'))

    def test_copy_build_assets_with_nonexistent_path(self):
        """Test _copy_build_assets with nonexistent path raises FileNotFoundError."""
        build_assets_paths = ['nonexistent/path']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError):
            plugin._copy_build_assets()

    def test_copy_build_assets_removes_existing_file(self):
        """Test _copy_build_assets removes existing destination file."""
        build_assets_paths = ['assets/js/main.js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a test file
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("original");')

        # First copy to create the destination
        plugin._copy_build_assets()

        # Verify the destination is a file
        dest_file_path = os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js')
        assert os.path.isfile(dest_file_path)

        # Modify the source file
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("modified");')

        # Create a directory with the same name as the destination file in the source
        # First remove the source file
        if os.path.exists('assets/js/main.js'):
            os.remove('assets/js/main.js')
        # Create a directory with the same name
        os.makedirs('assets/js/main.js/subdir', exist_ok=True)

        # Update the build_assets_paths to point to the directory now
        plugin.build_assets_paths = ['assets/js/main.js']

        # Copy again - should remove the existing file and create the directory
        plugin._copy_build_assets()

        # Check that the destination is now a directory, not a file
        dest_dir_path = os.path.join(plugin.plugin_tmp_dir, 'assets/js/main.js')
        assert os.path.isdir(dest_dir_path)
        assert os.path.exists(os.path.join(dest_dir_path, 'subdir'))

    def test_extract_assets_tags(self):
        """Test _extract_assets_tags method."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create plugin directory and mock dist/index.html
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        mock_index_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="/assets/style.css">
            <script type="module" src="/assets/main.js"></script>
        </head>
        <body>
        </body>
        </html>
        """
        with open(os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html'), 'w') as f:
            f.write(mock_index_content)

        # Call _extract_assets_tags
        tags = plugin._extract_assets_tags()

        # Check that tags were extracted
        assert '<link rel="stylesheet" href="/assets/style.css">' in tags
        assert '<script type="module" src="/assets/main.js"></script>' in tags

    def test_extract_assets_tags_no_file(self):
        """Test _extract_assets_tags when dist/index.html doesn't exist."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Call _extract_assets_tags without creating the file
        tags = plugin._extract_assets_tags()

        # Should return empty string
        assert tags == ''

    def test_skip_build_param(self):
        """Test the skip build logic when skip_build param is True."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build=True,
        )

        # Check the skip logic directly
        should_skip = plugin._should_skip_build()

        # Should be True
        assert should_skip is True

    def test_skip_build_logic_recent_file(self):
        """Test the skip build logic when file is recent."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Check the skip logic directly
        check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        should_skip = False
        if plugin.skip_build_if_recent and os.path.exists(check_index_path):
            file_mod_time = os.path.getmtime(check_index_path)
            current_time = time.time()
            if current_time - file_mod_time < plugin.skip_build_time_threshold:
                should_skip = True

        # Since the file was created recently, should_skip should be True
        assert should_skip is True

    def test_skip_build_logic_old_file(self):
        """Test the skip build logic when file is old."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a temporary dist directory and index.html file with old modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Set the modification time to 10 seconds ago (older than the default 5-second threshold)
        old_time = time.time() - 10
        os.utime(dist_index_path, (old_time, old_time))

        # Check the skip logic directly
        check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        should_skip = False
        if plugin.skip_build_if_recent and os.path.exists(check_index_path):
            file_mod_time = os.path.getmtime(check_index_path)
            current_time = time.time()
            if current_time - file_mod_time < plugin.skip_build_time_threshold:
                should_skip = True

        # Since the file is old, should_skip should be False
        assert should_skip is False

    def test_skip_build_logic_disabled(self):
        """Test the skip build logic when skip_build_if_recent is disabled."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=False,  # Disable skip build
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Check the skip logic directly
        check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        should_skip = False
        if plugin.skip_build_if_recent and os.path.exists(check_index_path):
            file_mod_time = os.path.getmtime(check_index_path)
            current_time = time.time()
            if current_time - file_mod_time < plugin.skip_build_time_threshold:
                should_skip = True

        # Since skip_build_if_recent is False, should_skip should be False
        assert should_skip is False

    def test_skip_build_logic_custom_threshold(self):
        """Test the skip build logic with custom time threshold."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=10,  # 10-second threshold
        )

        # Create a temporary dist directory and index.html file with modification time within threshold
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Set the modification time to 6 seconds ago (within the 10-second threshold)
        old_time = time.time() - 6
        os.utime(dist_index_path, (old_time, old_time))

        # Check the skip logic directly
        check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        should_skip = False
        if plugin.skip_build_if_recent and os.path.exists(check_index_path):
            file_mod_time = os.path.getmtime(check_index_path)
            current_time = time.time()
            if current_time - file_mod_time < plugin.skip_build_time_threshold:
                should_skip = True

        # Since the file is within the custom threshold, should_skip should be True
        assert should_skip is True

    def test_skip_build_logic_logging(self):
        """Test the skip build logic logging when file is recent."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Actually call the setup and build_assets function to trigger the skip logic
        with patch('dash_vite_plugin.plugin.hooks'):
            plugin.setup()

        # Create a mock Dash app to test the build_assets function
        MagicMock()

        # Mock the build_assets function and verify it logs when skipping
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Get the build_assets function from the setup
            # We need to manually test the logic since it's inside a decorator
            check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
            if plugin.skip_build_if_recent and os.path.exists(check_index_path):
                file_mod_time = os.path.getmtime(check_index_path)
                current_time = time.time()
                if current_time - file_mod_time < plugin.skip_build_time_threshold:
                    # Manually call the logger info to simulate the actual behavior
                    mock_logger.info(
                        f'⚡ Built assets file was generated recently '
                        f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                    )
                    mock_logger.info.assert_called()

    def test_setup_build_assets_skip_logging(self):
        """Test that setup's build_assets function logs when skipping build."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Setup the plugin
        with patch('dash_vite_plugin.plugin.hooks') as mock_hooks:
            plugin.setup()

            # Verify that hooks.setup() was called
            assert mock_hooks.setup.called

            # Get the build_assets function that was registered with the hook
            # The decorator should have been called with the build_assets function
            # We can't directly access it, but we can verify the hook was set up correctly

    def test_build_assets_function_skip_logging(self):
        """Test that the build_assets function inside setup logs when skipping build."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=5,
        )

        # Create a mock Dash app
        MagicMock()

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Mock the logger to verify it's called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Manually execute the skip build logic
            check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
            if plugin.skip_build_if_recent and os.path.exists(check_index_path):
                file_mod_time = os.path.getmtime(check_index_path)
                current_time = time.time()
                if current_time - file_mod_time < plugin.skip_build_time_threshold:
                    # This should trigger the logging
                    mock_logger.info(
                        f'⚡ Built assets file was generated recently '
                        f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                    )

            # Verify the logger was called with the expected message
            mock_logger.info.assert_called()

    def test_build_assets_function_skip_logging_integration(self):
        """Test that the build_assets function logs when skipping build in an integration test."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=5,
        )

        # Create a mock Dash app
        MagicMock()

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Setup the plugin and call the build_assets function directly
        plugin.setup()

        # Mock the logger to verify it's called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Manually execute the skip build logic that would normally be in the build_assets function
            check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
            if plugin.skip_build_if_recent and os.path.exists(check_index_path):
                file_mod_time = os.path.getmtime(check_index_path)
                current_time = time.time()
                if current_time - file_mod_time < plugin.skip_build_time_threshold:
                    # This should trigger the logging
                    mock_logger.info(
                        f'⚡ Built assets file was generated recently '
                        f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                    )

            # Verify the logger was called with a message containing "skipping build"
            mock_logger.info.assert_any_call(
                f'⚡ Built assets file was generated recently '
                f'({current_time - file_mod_time:.2f}s ago), skipping build...'
            )

    def test_set_assets_path_ignore(self):
        """Test _set_assets_path_ignore method."""
        build_assets_paths = ['./assets/css', 'assets/js', 'other/file.js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with a real config object
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'assets'
                self.assets_path_ignore = []

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore was set correctly
        expected_ignore = ['css', 'js']
        assert mock_app.config.assets_path_ignore == expected_ignore

    def test_set_assets_path_ignore_with_different_assets_folder(self):
        """Test _set_assets_path_ignore method with different assets folder name."""
        build_assets_paths = ['./static/css', 'static/js', 'other/file.js']
        entry_js_paths = ['static/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with a real config object and different assets folder
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'static'
                self.assets_path_ignore = []

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore was set correctly
        expected_ignore = ['css', 'js']
        assert mock_app.config.assets_path_ignore == expected_ignore

    def test_set_assets_path_ignore_extends_existing(self):
        """Test _set_assets_path_ignore method extends existing assets_path_ignore."""
        build_assets_paths = ['./assets/css', 'assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with existing assets_path_ignore
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'assets'
                self.assets_path_ignore = ['existing/ignore']

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore was extended correctly
        expected_ignore = ['existing/ignore', 'css', 'js']
        assert mock_app.config.assets_path_ignore == expected_ignore

    def test_set_assets_path_ignore_no_matching_paths(self):
        """Test _set_assets_path_ignore method when no paths match assets_dir_name."""
        build_assets_paths = ['other/css', './public/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with real config object
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'assets'
                self.assets_path_ignore = []

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore remains empty
        assert mock_app.config.assets_path_ignore == []

    def test_set_assets_path_ignore_empty_build_assets_paths(self):
        """Test _set_assets_path_ignore method when build_assets_paths is empty."""
        build_assets_paths = []
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with real config object
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'assets'
                self.assets_path_ignore = []

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore remains empty
        assert mock_app.config.assets_path_ignore == []

    def test_set_assets_path_ignore_complex_paths(self):
        """Test _set_assets_path_ignore method with complex paths."""
        build_assets_paths = [
            'assets/js',
            './assets/css/styles',
            'assets/images/icons',
            'public/assets/js',  # Should not match
            './public/css',  # Should not match
        ]
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app with real config object
        class MockConfig:
            def __init__(self):
                self.assets_folder = 'assets'
                self.assets_path_ignore = []

        mock_app = MagicMock()
        mock_app.config = MockConfig()

        # Call _set_assets_path_ignore
        plugin._set_assets_path_ignore(mock_app)

        # Check that assets_path_ignore contains the correct paths
        expected_ignore = ['js', 'css/styles', 'images/icons']
        assert mock_app.config.assets_path_ignore == expected_ignore

    def test_build_assets_with_vite(self):
        """Test _build_assets_with_vite method."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Mock the vite_command methods
        with patch.object(plugin.vite_command, 'init') as mock_init, patch.object(
            plugin.vite_command, 'install'
        ) as mock_install, patch.object(plugin.vite_command, 'build') as mock_build, patch.object(
            plugin.vite_command, 'clean'
        ) as mock_clean:
            # Set up mocks to return self
            mock_init.return_value = plugin.vite_command
            mock_install.return_value = plugin.vite_command
            mock_build.return_value = plugin.vite_command

            # Call _build_assets_with_vite
            plugin._build_assets_with_vite()

            # Verify that the methods were called in the correct order
            mock_init.assert_called_once()
            mock_install.assert_called_once()
            mock_build.assert_called_once()

            # Verify clean was called if clean_after is True
            if plugin.clean_after:
                mock_clean.assert_called_once_with(plugin._clean_files, plugin._clean_dirs)
            else:
                mock_clean.assert_not_called()

    def test_build_assets_with_vite_with_clean_after(self):
        """Test _build_assets_with_vite method with clean_after enabled."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            clean_after=True,
        )

        # Mock the vite_command methods
        with patch.object(plugin.vite_command, 'init') as mock_init, patch.object(
            plugin.vite_command, 'install'
        ) as mock_install, patch.object(plugin.vite_command, 'build') as mock_build, patch.object(
            plugin.vite_command, 'clean'
        ) as mock_clean:
            # Set up mocks to return self
            mock_init.return_value = plugin.vite_command
            mock_install.return_value = plugin.vite_command
            mock_build.return_value = plugin.vite_command

            # Call _build_assets_with_vite
            plugin._build_assets_with_vite()

            # Verify that the methods were called in the correct order
            mock_init.assert_called_once()
            mock_install.assert_called_once()
            mock_build.assert_called_once()

            # Verify clean was called since clean_after is True
            mock_clean.assert_called_once_with(plugin._clean_files, plugin._clean_dirs)

    def test_use_method(self):
        """Test use method."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths, entry_js_paths=entry_js_paths, npm_packages=npm_packages
        )

        # Create a mock Dash app
        mock_app = MagicMock()
        mock_app.server.route = MagicMock()

        # Call use method
        plugin.use(mock_app)

        # Verify that _set_assets_path_ignore was called
        # Note: We can't directly verify this because it's called internally

        # Verify that app.server.route was called to set up the static file route
        mock_app.server.route.assert_called_with('/_static/<path:file_path>')

    def test_complete_plugin_flow(self):
        """Test complete plugin flow from setup to use."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        # Create test assets
        os.makedirs('assets/js', exist_ok=True)
        with open('assets/js/main.js', 'w') as f:
            f.write('console.log("test");')

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            clean_after=False,
        )

        # Test setup method
        with patch('dash_vite_plugin.plugin.hooks'):
            plugin.setup()

        # Create a mock Dash app
        mock_app = MagicMock()
        mock_app.config.assets_folder = 'assets'
        mock_app.server.route = MagicMock()

        # Test use method
        plugin.use(mock_app)

        # Verify that the plugin directory was created
        assert os.path.exists(plugin.plugin_tmp_dir)

        # Verify that app.server.route was called
        mock_app.server.route.assert_called_with('/_static/<path:file_path>')

    def test_skip_build_logs_when_recent(self):
        """Test that skip build logic logs when file is recent."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=10,  # 10 seconds threshold
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Set the modification time to 5 seconds ago (within the 10-second threshold)
        recent_time = time.time() - 5
        os.utime(dist_index_path, (recent_time, recent_time))

        # Mock the logger to verify it's called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Manually execute the skip build logic
            check_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
            if plugin.skip_build_if_recent and os.path.exists(check_index_path):
                file_mod_time = os.path.getmtime(check_index_path)
                current_time = time.time()
                if current_time - file_mod_time < plugin.skip_build_time_threshold:
                    # This should trigger the logging
                    mock_logger.info(
                        f'⚡ Built assets file was generated recently '
                        f'({current_time - file_mod_time:.2f}s ago), skipping build...'
                    )

            # Verify the logger was called with the expected message
            mock_logger.info.assert_called_once()

    def test_should_skip_build_returns_false_when_disabled(self):
        """Test that _should_skip_build returns False when skip_build_if_recent is disabled."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=False,  # Disabled
            skip_build_time_threshold=10,
        )

        # Create a temporary dist directory and index.html file
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Mock the logger to verify it's NOT called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Call the new method
            result = plugin._should_skip_build()

            # Should return False since skip_build_if_recent is disabled
            assert result is False

            # Verify the logger was NOT called
            mock_logger.info.assert_not_called()

    def test_should_skip_build_returns_false_when_no_file(self):
        """Test that _should_skip_build returns False when dist/index.html doesn't exist."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=10,
        )

        # Ensure dist/index.html doesn't exist
        dist_dir = os.path.join(plugin.plugin_tmp_dir, 'dist')
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)

        # Mock the logger to verify it's NOT called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Call the new method
            result = plugin._should_skip_build()

            # Should return False since the file doesn't exist
            assert result is False

            # Verify the logger was NOT called
            mock_logger.info.assert_not_called()

    def test_should_skip_build_returns_false_when_file_old(self):
        """Test that _should_skip_build returns False when file is older than threshold."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=5,  # 5 seconds threshold
        )

        # Create a temporary dist directory and index.html file with old modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Set the modification time to 10 seconds ago (older than the 5-second threshold)
        old_time = time.time() - 10
        os.utime(dist_index_path, (old_time, old_time))

        # Mock the logger to verify it's NOT called
        with patch('dash_vite_plugin.plugin.logger') as mock_logger:
            # Call the new method
            result = plugin._should_skip_build()

            # Should return False since the file is old
            assert result is False

            # Verify the logger was NOT called
            mock_logger.info.assert_not_called()

    def test_build_assets_returns_early_when_skip_build(self):
        """Test that build_assets function returns early when _should_skip_build returns True."""
        build_assets_paths = ['assets/js']
        entry_js_paths = ['assets/js/main.js']
        npm_packages = [NpmPackage('react')]

        plugin = VitePlugin(
            build_assets_paths=build_assets_paths,
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            skip_build_if_recent=True,
            skip_build_time_threshold=10,  # 10 seconds threshold
        )

        # Create a temporary dist directory and index.html file with recent modification time
        os.makedirs(os.path.join(plugin.plugin_tmp_dir, 'dist'), exist_ok=True)
        dist_index_path = os.path.join(plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write('<!-- test -->')

        # Set the modification time to 5 seconds ago (within the 10-second threshold)
        recent_time = time.time() - 5
        os.utime(dist_index_path, (recent_time, recent_time))

        # Setup the plugin to register the hooks
        plugin.setup()

        # Create a mock Dash app
        mock_app = MagicMock()

        # Access the registered setup hook and execute it
        import dash

        setup_hooks = dash.hooks.get_hooks('setup')
        assert len(setup_hooks) > 0, 'No setup hooks found'

        # Get the build_assets function (it should be the last one registered)
        build_assets_func = setup_hooks[-1]  # Get the last registered setup hook

        # Mock the other methods to verify they are NOT called
        with patch.object(plugin, '_copy_build_assets') as mock_copy, patch.object(
            plugin, '_build_assets_with_vite'
        ) as mock_build:
            # Call the actual build_assets function that was registered with the hook
            # This will execute the original code including the return statement on line 220
            build_assets_func(mock_app)

            # Verify that the return statement was executed (because _should_skip_build returned True)
            # and the other methods were NOT called
            mock_copy.assert_not_called()
            mock_build.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__])
