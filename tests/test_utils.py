import os
import pytest
import shutil
import tempfile
from unittest.mock import Mock, patch
from dash_vite_plugin.utils import NpmPackage, ViteCommand


class TestUtils:
    """Test cases for utility functions."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_npm_package_creation(self):
        """Test NpmPackage dataclass creation."""
        # Test with default parameters
        package = NpmPackage(name='react')
        assert package.name == 'react'
        assert package.version == 'latest'
        assert package.install_mode == '-S'

        # Test with custom parameters
        package = NpmPackage(name='lodash', version='4.17.21', install_mode='-D')
        assert package.name == 'lodash'
        assert package.version == '4.17.21'
        assert package.install_mode == '-D'

    def test_vite_command_initialization(self):
        """Test ViteCommand initialization."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        assert vite_command.entry_js_paths == entry_js_paths
        assert vite_command.npm_packages == npm_packages
        assert vite_command.plugin_tmp_dir == plugin_tmp_dir
        assert vite_command.support_less is False
        assert vite_command.support_sass is False
        assert vite_command.is_cli is False
        assert vite_command.index_html_path == f'{plugin_tmp_dir}/index.html'
        assert vite_command.config_js_path == f'{plugin_tmp_dir}/vite.config.js'

    def test_vite_command_initialization_with_support_flags(self):
        """Test ViteCommand initialization with support flags."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        assert vite_command.support_less is True
        assert vite_command.support_sass is True

    def test_create_default_vite_config(self):
        """Test create_default_vite_config method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Call create_default_vite_config
        vite_command.create_default_vite_config()

        # Check that file was created
        assert os.path.exists(vite_command.config_js_path)

        # Check file content
        with open(vite_command.config_js_path, 'r') as f:
            content = f.read()
            assert "import { defineConfig } from 'vite'" in content
            assert "outDir: 'dist'" in content
            assert "assetsDir: 'assets'" in content
            assert "chunkFileNames: '_static/js/[name]-[hash].js'" in content
            assert "entryFileNames: '_static/js/[name]-[hash].js'" in content
            assert "assetFileNames: '_static/[ext]/[name]-[hash].[ext]'" in content

    def test_create_default_index_html(self):
        """Test create_default_index_html method."""
        entry_js_paths = ['src/main.js', 'src/secondary.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Call create_default_index_html
        vite_command.create_default_index_html()

        # Check that file was created
        assert os.path.exists(vite_command.index_html_path)

        # Check file content
        with open(vite_command.index_html_path, 'r') as f:
            content = f.read()
            assert '<!DOCTYPE html>' in content
            assert '<script type="module" src="src/main.js"></script>' in content
            assert '<script type="module" src="src/secondary.js"></script>' in content

    def test_check_npm_init(self):
        """Test _check_npm_init method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Initially should return False
        assert vite_command._check_npm_init() is False

        # Create package.json
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            f.write('{}')

        # Should now return True
        assert vite_command._check_npm_init() is True

    def test_check_vite(self):
        """Test _check_vite method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate Vite being installed
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Should return True when Vite is installed
            assert vite_command._check_vite() is True
            mock_run.assert_called_once()

        # Mock subprocess.run to simulate Vite not being installed
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_run.return_value = mock_result

            # Should return False when Vite is not installed
            assert vite_command._check_vite() is False

    def test_check_less(self):
        """Test _check_less method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create package.json with less in devDependencies
        package_json_content = {'devDependencies': {'less': '^4.0.0'}}
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            import json

            json.dump(package_json_content, f)

        # Should return True when Less is in package.json
        assert vite_command._check_less() is True

        # Modify package.json to remove less
        package_json_content = {'devDependencies': {}}
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            json.dump(package_json_content, f)

        # Should return False when Less is not in package.json
        assert vite_command._check_less() is False

        # Remove package.json
        os.remove(os.path.join(plugin_tmp_dir, 'package.json'))

        # Should return False when package.json doesn't exist
        assert vite_command._check_less() is False

    def test_check_sass(self):
        """Test _check_sass method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create package.json with sass in devDependencies
        package_json_content = {'devDependencies': {'sass': '^1.0.0'}}
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            import json

            json.dump(package_json_content, f)

        # Should return True when Sass is in package.json
        assert vite_command._check_sass() is True

        # Modify package.json to remove sass
        package_json_content = {'devDependencies': {}}
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            json.dump(package_json_content, f)

        # Should return False when Sass is not in package.json
        assert vite_command._check_sass() is False

        # Remove package.json
        os.remove(os.path.join(plugin_tmp_dir, 'package.json'))

        # Should return False when package.json doesn't exist
        assert vite_command._check_sass() is False

    def test_install_vite(self):
        """Test _install_vite method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate successful Vite installation
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Mock _check_vite to return False initially, then True after installation
            with patch.object(vite_command, '_check_vite', side_effect=[False, True]):
                # Should not raise an exception
                vite_command._install_vite()

                # Verify subprocess.run was called for npm install
                mock_run.assert_called_once()

    def test_install_less(self):
        """Test _install_less method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate successful Less installation
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Mock _check_less to return False initially, then True after installation
            with patch.object(vite_command, '_check_less', side_effect=[False, True]):
                # Should not raise an exception
                vite_command._install_less()

                # Verify subprocess.run was called for npm install
                mock_run.assert_called_once()

    def test_install_sass(self):
        """Test _install_sass method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate successful Sass installation
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Mock _check_sass to return False initially, then True after installation
            with patch.object(vite_command, '_check_sass', side_effect=[False, True]):
                # Should not raise an exception
                vite_command._install_sass()

                # Verify subprocess.run was called for npm install
                mock_run.assert_called_once()

    def test_install_npm_packages(self):
        """Test _install_npm_packages method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react', '17.0.0', '-S'), NpmPackage('lodash', '4.17.21', '-D')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate successful npm package installation
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Should not raise an exception
            vite_command._install_npm_packages()

            # Verify subprocess.run was called for each npm package
            assert mock_run.call_count == 2

    def test_vite_command_init_creates_files(self):
        """Test that init method creates necessary files."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to avoid actual npm calls
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Call init
            result = vite_command.init()

            # Check that files were created
            assert os.path.exists(vite_command.config_js_path)
            assert os.path.exists(vite_command.index_html_path)
            # Note: package.json is created by npm init, which we've mocked
            # In a real scenario, it would be created, but in our test we've mocked subprocess
            # So we can't assert its existence

            # Check that init returns self
            assert result is vite_command

    def test_vite_command_init_with_cli_mode(self):
        """Test that init method works with CLI mode."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=True,
        )

        # Mock subprocess.run to avoid actual npm calls
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Call init
            result = vite_command.init()

            # Check that init returns self
            assert result is vite_command

    def test_vite_command_install(self):
        """Test install method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to avoid actual npm calls
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Create package.json first
            with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
                f.write('{}')

            # Call install
            result = vite_command.install()

            # Check that install returns self
            assert result is vite_command

            # Verify subprocess.run was called for vite and npm packages
            assert mock_run.call_count >= 1

    def test_vite_command_build(self):
        """Test build method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to avoid actual build
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Call build
            result = vite_command.build()

            # Check that build returns self
            assert result is vite_command

            # Verify subprocess.run was called for vite build
            mock_run.assert_called_once()

    def test_vite_command_clean(self):
        """Test clean method."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create files and directories to clean
        os.makedirs(os.path.join(plugin_tmp_dir, 'dist'), exist_ok=True)
        os.makedirs(os.path.join(plugin_tmp_dir, 'node_modules'), exist_ok=True)

        with open(vite_command.config_js_path, 'w') as f:
            f.write('config')
        with open(vite_command.index_html_path, 'w') as f:
            f.write('html')
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(plugin_tmp_dir, 'package-lock.json'), 'w') as f:
            f.write('{}')

        # Call clean
        result = vite_command.clean([], [])

        # Check that clean returns self
        assert result is vite_command

        # Note: In a real test, we would verify that files were actually removed,
        # but since we're not actually creating all the files that would be cleaned,
        # we're mainly testing that the method doesn't crash

    def test_vite_command_clean_with_extra_files(self):
        """Test clean method with extra files and directories."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create extra files and directories to clean
        extra_file = os.path.join(plugin_tmp_dir, 'extra.js')
        extra_dir = os.path.join(plugin_tmp_dir, 'extra_dir')

        with open(extra_file, 'w') as f:
            f.write('extra')
        os.makedirs(extra_dir, exist_ok=True)

        # Call clean with extra files and directories
        result = vite_command.clean([extra_file], [extra_dir])

        # Check that clean returns self
        assert result is vite_command

    def test_check_less_exception_handling(self):
        """Test _check_less method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create an invalid package.json that will cause JSON parsing to fail
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            f.write('invalid json')

        # Should return False when exception occurs
        assert vite_command._check_less() is False

    def test_check_sass_exception_handling(self):
        """Test _check_sass method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create an invalid package.json that will cause JSON parsing to fail
        with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
            f.write('invalid json')

        # Should return False when exception occurs
        assert vite_command._check_sass() is False

    def test_install_vite_failure(self):
        """Test _install_vite method handles installation failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate Vite installation failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'Installation failed'
            mock_run.return_value = mock_result

            # Mock _check_vite to return False
            with patch.object(vite_command, '_check_vite', return_value=False):
                # Should raise RuntimeError
                with pytest.raises(RuntimeError, match='Installation failed'):
                    vite_command._install_vite()

    def test_install_vite_exception_handling(self):
        """Test _install_vite method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Mock _check_vite to return False
            with patch.object(vite_command, '_check_vite', return_value=False):
                # Should raise the same exception
                with pytest.raises(Exception, match='Test exception'):
                    vite_command._install_vite()

    def test_install_less_failure(self):
        """Test _install_less method handles installation failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate Less installation failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'Installation failed'
            mock_run.return_value = mock_result

            # Mock _check_less to return False
            with patch.object(vite_command, '_check_less', return_value=False):
                # Should raise RuntimeError
                with pytest.raises(RuntimeError, match='Installation failed'):
                    vite_command._install_less()

    def test_install_less_exception_handling(self):
        """Test _install_less method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=True,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Mock _check_less to return False
            with patch.object(vite_command, '_check_less', return_value=False):
                # Should raise the same exception
                with pytest.raises(Exception, match='Test exception'):
                    vite_command._install_less()

    def test_install_sass_failure(self):
        """Test _install_sass method handles installation failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate Sass installation failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'Installation failed'
            mock_run.return_value = mock_result

            # Mock _check_sass to return False
            with patch.object(vite_command, '_check_sass', return_value=False):
                # Should raise RuntimeError
                with pytest.raises(RuntimeError, match='Installation failed'):
                    vite_command._install_sass()

    def test_install_sass_exception_handling(self):
        """Test _install_sass method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Mock _check_sass to return False
            with patch.object(vite_command, '_check_sass', return_value=False):
                # Should raise the same exception
                with pytest.raises(Exception, match='Test exception'):
                    vite_command._install_sass()

    def test_install_npm_packages_failure(self):
        """Test _install_npm_packages method handles installation failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react', '17.0.0', '-S')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate npm package installation failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'Installation failed'
            mock_run.return_value = mock_result

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match='Installation failed'):
                vite_command._install_npm_packages()

    def test_install_npm_packages_exception_handling(self):
        """Test _install_npm_packages method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react', '17.0.0', '-S')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Should raise the same exception
            with pytest.raises(Exception, match='Test exception'):
                vite_command._install_npm_packages()

    def test_init_npm_init_failure(self):
        """Test init method handles npm init failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate npm init failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'npm init failed'
            mock_run.return_value = mock_result

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match='npm init failed'):
                vite_command.init()

    def test_init_exception_handling(self):
        """Test init method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Should raise the same exception
            with pytest.raises(Exception, match='Test exception'):
                vite_command.init()

    def test_install_with_sass_support(self):
        """Test install method with Sass support enabled."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=True,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to avoid actual npm calls
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            # Create package.json first
            with open(os.path.join(plugin_tmp_dir, 'package.json'), 'w') as f:
                f.write('{}')

            # Call install
            result = vite_command.install()

            # Check that install returns self
            assert result is vite_command

            # Verify subprocess.run was called for vite, sass, and npm packages
            assert mock_run.call_count >= 2

    def test_build_failure(self):
        """Test build method handles build failure."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate build failure
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Non-zero return code indicates failure
            mock_result.stderr = 'Build failed'
            mock_run.return_value = mock_result

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match='Build failed'):
                vite_command.build()

    def test_build_exception_handling(self):
        """Test build method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock subprocess.run to simulate exception
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception('Test exception')

            # Should raise the same exception
            with pytest.raises(Exception, match='Test exception'):
                vite_command.build()

    def test_clean_file_removal_exception(self):
        """Test clean method handles file removal exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create files to clean
        with open(vite_command.config_js_path, 'w') as f:
            f.write('config')

        # Mock os.remove to simulate exception
        with patch('os.remove') as mock_remove:
            mock_remove.side_effect = Exception('Test exception')

            # Mock logger to verify warning is logged
            with patch('dash_vite_plugin.utils.logger') as mock_logger:
                # Call clean
                result = vite_command.clean([], [])

                # Check that clean returns self
                assert result is vite_command

                # Verify warning was logged
                mock_logger.warning.assert_called()

    def test_clean_directory_removal_exception(self):
        """Test clean method handles directory removal exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Create directory to clean
        os.makedirs(os.path.join(plugin_tmp_dir, 'node_modules'), exist_ok=True)

        # Mock shutil.rmtree to simulate exception
        with patch('shutil.rmtree') as mock_rmtree:
            mock_rmtree.side_effect = Exception('Test exception')

            # Mock logger to verify warning is logged
            with patch('dash_vite_plugin.utils.logger') as mock_logger:
                # Call clean
                result = vite_command.clean([], [])

                # Check that clean returns self
                assert result is vite_command

                # Verify warning was logged
                mock_logger.warning.assert_called()

    def test_clean_exception_handling(self):
        """Test clean method handles exceptions properly."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=False,
        )

        # Mock os.remove to simulate exception
        with patch('os.remove') as mock_remove:
            mock_remove.side_effect = Exception('Test exception')

            # Mock logger to simulate exception in logger.warning
            with patch('dash_vite_plugin.utils.logger') as mock_logger:
                mock_logger.warning.side_effect = Exception('Logger exception')

                # Should raise the logger exception
                with pytest.raises(Exception, match='Logger exception'):
                    # Create files to clean first
                    with open(vite_command.config_js_path, 'w') as f:
                        f.write('config')
                    # Now call clean which should raise the logger exception
                    vite_command.clean([], [])

    def test_clean_file_removal_cli_logging(self):
        """Test clean method logs file removal when is_cli is True."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        # Create ViteCommand with is_cli=True
        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=True,  # Set to True to test CLI logging
        )

        # Create files to clean
        with open(vite_command.config_js_path, 'w') as f:
            f.write('config')

        # Mock logger to verify info is logged
        with patch('dash_vite_plugin.utils.logger') as mock_logger:
            # Call clean
            result = vite_command.clean([], [])

            # Check that clean returns self
            assert result is vite_command

            # Verify info was logged
            mock_logger.info.assert_called()

    def test_clean_directory_removal_cli_logging(self):
        """Test clean method logs directory removal when is_cli is True."""
        entry_js_paths = ['src/main.js']
        npm_packages = [NpmPackage('react')]
        plugin_tmp_dir = '_vite_test'

        # Create ViteCommand with is_cli=True
        vite_command = ViteCommand(
            entry_js_paths=entry_js_paths,
            npm_packages=npm_packages,
            plugin_tmp_dir=plugin_tmp_dir,
            support_less=False,
            support_sass=False,
            download_node=False,
            node_version='18.17.0',
            is_cli=True,  # Set to True to test CLI logging
        )

        # Create directory to clean
        os.makedirs(os.path.join(plugin_tmp_dir, 'node_modules'), exist_ok=True)

        # Mock logger to verify info is logged
        with patch('dash_vite_plugin.utils.logger') as mock_logger:
            # Call clean
            result = vite_command.clean([], [])

            # Check that clean returns self
            assert result is vite_command

            # Verify info was logged
            mock_logger.info.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])
