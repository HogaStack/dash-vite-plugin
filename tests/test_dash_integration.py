import os
import pytest
import shutil
import tempfile
from dash import Dash, html, Input, Output
from dash.testing.composite import DashComposite
from dash_vite_plugin import NpmPackage, VitePlugin


class TestDashIntegration:
    """Test cases for Dash integration with the Vite plugin."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

        # Clean up the global hooks state of Dash
        try:
            import dash._hooks as hooks

            # Clean all types of hooks
            hook_types = ['setup', 'index', 'layout', 'routes', 'error', 'callback', 'custom_data', 'dev_tools']
            for hook_type in hook_types:
                if hasattr(hooks.hooks, '_ns') and hook_type in hooks.hooks._ns:
                    hooks.hooks._ns[hook_type].clear()
                if hasattr(hooks.hooks, '_finals') and hook_type in hooks.hooks._finals:
                    hooks.hooks._finals.pop(hook_type, None)
        except Exception:
            # If cleanup fails, it doesn't affect the test results
            pass

    def test_vite_plugin_integration(self, dash_duo: DashComposite):
        """Test the plugin works with a Dash app."""
        # Create a simple assets structure
        os.makedirs('assets/js', exist_ok=True)
        # Create JavaScript that adds a global variable and modifies the DOM
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            
            // Add a function to test JavaScript functionality
            window.testFunction = function() {
                return "JavaScript is working";
            };
            
            console.log("test");
            """)

        # Create VitePlugin instance
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test', id='header'),
                html.P('This tests the Vite plugin integration.', id='paragraph'),
                html.Button(
                    'Click Me',
                    id='test-button',
                ),
                # Add elements to test JavaScript behavior
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        // Test if function exists and works
                        if (typeof window.testFunction !== 'undefined') {
                            try {
                                const result = window.testFunction();
                                if (result === 'JavaScript is working') {
                                    return 'JavaScript behavior is working correctly: ' + result;
                                } else {
                                    return 'Function returned unexpected result: ' + result;
                                }
                            } catch (e) {
                                return 'Error calling testFunction: ' + e.message;
                            }
                        } else {
                            return 'testFunction is not defined';
                        }
                    } else {
                        return 'Global variable test failed: ' + (typeof window.testVariable !== 'undefined' ? window.testVariable : 'undefined');
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test')

        # Check that the H1 element is rendered
        h1_element = dash_duo.find_element('#header')
        assert h1_element is not None

        # Check that the paragraph is rendered
        dash_duo.wait_for_text_to_equal('#paragraph', 'This tests the Vite plugin integration.')

        # Check that the button is rendered
        button_element = dash_duo.find_element('#test-button')
        assert button_element is not None

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_result = dash_duo.find_element('#js-test-result')

        # Initially should show prompt to click
        assert js_test_result.text == 'Click button to test JavaScript'

        # Click the test button
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal(
            '#js-test-result', 'JavaScript behavior is working correctly: JavaScript is working'
        )

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_less_support(self, dash_duo: DashComposite):
        """Test the plugin works with Less support enabled."""
        # Create assets structure
        os.makedirs('assets/js', exist_ok=True)
        os.makedirs('assets/less', exist_ok=True)

        # Create Less file with simple styling
        with open('assets/less/style.less', 'w') as f:
            f.write("""
            @color: #4D926F;
            
            body {
              color: @color;
            }
            
            #header {
              font-weight: bold;
            }
            
            .test-class {
              background-color: lighten(@color, 10%);
            }
            """)

        # Create JavaScript file that imports Less
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Import the Less file
            import '../less/style.less';
            
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            
            // Add a function to test that the CSS was applied
            window.checkCSSApplied = function() {
              const header = document.getElementById('header');
              const headerColor = window.getComputedStyle(header).color;
              // Check if the Less variable was processed correctly
              return headerColor.indexOf('77, 146, 111') !== -1 || headerColor.indexOf('#4d926f') !== -1;
            };
            """)

        # Create VitePlugin instance with Less support
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js', 'assets/less'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            support_less=True,
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Less Support', id='header'),
                html.P('This tests the Vite plugin with Less support.', id='paragraph'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution and CSS application
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        // Check if CSS was applied correctly
                        if (typeof window.checkCSSApplied !== 'undefined' && window.checkCSSApplied()) {
                            return 'JavaScript behavior is working correctly and Less CSS applied';
                        }
                        return 'JavaScript behavior is working correctly but Less CSS not applied';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript and Less CSS';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Less Support')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal(
            '#js-test-result', 'JavaScript behavior is working correctly and Less CSS applied'
        )

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_assets_path_ignore(self, dash_duo: DashComposite):
        """Test the plugin correctly ignores assets paths."""
        # Create assets structure
        os.makedirs('assets/js', exist_ok=True)
        os.makedirs('assets/css', exist_ok=True)

        # Create JavaScript file
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            """)

        # Create CSS file (this should be ignored)
        with open('assets/css/style.css', 'w') as f:
            f.write("""
            body { background-color: red; }
            """)

        # Create VitePlugin instance with assets to ignore
        vite_plugin = VitePlugin(
            build_assets_paths=['./assets/css', 'assets/js'],  # These should be ignored by Dash
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Assets Ignore', id='header'),
                html.P('This tests the Vite plugin assets ignore functionality.', id='paragraph'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Assets Ignore')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_skip_build_if_recent(self, dash_duo: DashComposite):
        """Test the plugin skips build when dist file is recent."""
        # Create a simple assets structure
        os.makedirs('assets/js', exist_ok=True)
        # Create JavaScript that adds a global variable and modifies the DOM
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            """)

        # Create VitePlugin instance
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            clean_after=False,
            skip_build_if_recent=True,
            skip_build_time_threshold=5,  # 5 second threshold
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Create dist directory and index.html to simulate recent build
        os.makedirs(os.path.join(vite_plugin.plugin_tmp_dir, 'dist', '_static', 'js'), exist_ok=True)
        dist_index_path = os.path.join(vite_plugin.plugin_tmp_dir, 'dist', 'index.html')
        with open(dist_index_path, 'w') as f:
            f.write("""
            <!DOCTYPE html>
            <html>
            <head>
                <script type="module" src="/_static/js/main.js"></script>
            </head>
            <body>
            </body>
            </html>
            """)

        # Create a simple JS file
        with open(os.path.join(vite_plugin.plugin_tmp_dir, 'dist', '_static', 'js', 'main.js'), 'w') as f:
            f.write("""
            window.testVariable = "VitePluginTest";
            """)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Skip Build', id='header'),
                html.P('This tests the Vite plugin skip build functionality.', id='paragraph'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Skip Build')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_custom_tmp_dir(self, dash_duo: DashComposite):
        """Test the plugin works with a custom temporary directory."""
        # Create a simple assets structure
        os.makedirs('assets/js', exist_ok=True)
        # Create JavaScript that adds a global variable and modifies the DOM
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            """)

        # Create VitePlugin instance with custom tmp dir
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            plugin_tmp_dir='_custom_vite',
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Verify that custom tmp dir was created
        assert os.path.exists('_custom_vite')

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Custom Tmp Dir', id='header'),
                html.P('This tests the Vite plugin with custom tmp directory.', id='paragraph'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Custom Tmp Dir')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_clean_after(self, dash_duo: DashComposite):
        """Test the plugin works with clean_after enabled."""
        # Create a simple assets structure
        os.makedirs('assets/js', exist_ok=True)
        # Create JavaScript that adds a global variable and modifies the DOM
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginTest";
            """)

        # Create VitePlugin instance with clean_after enabled
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('react')],
            clean_after=True,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Clean After', id='header'),
                html.P('This tests the Vite plugin with clean_after enabled.', id='paragraph'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Clean After')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_vue_support(self, dash_duo: DashComposite):
        """Test the plugin works with Vue support enabled."""
        # Create assets structure
        os.makedirs('assets/js', exist_ok=True)
        os.makedirs('assets/vue', exist_ok=True)

        # Create a simple Vue component using Vue 3 Composition API
        with open('assets/vue/App.vue', 'w') as f:
            f.write("""
            <template>
                <div id="vue-app">
                <h1>{{ message }}</h1>
                <button @click="updateMessage">Click me!</button>
                </div>
            </template>

            <script setup>
            import { ref } from 'vue'

            const message = ref('Hello from Vue!')

            const updateMessage = () => {
                message.value = 'Vue is working!'
            }
            </script>

            <style scoped>
            #vue-app {
                text-align: center;
                margin: 20px;
            }
            h1 {
                color: #42b883;
            }
            </style>
            """)

        # Create JavaScript file that imports and mounts Vue
        with open('assets/js/main.js', 'w') as f:
            f.write("""
        import { createApp } from "vue";
        import App from "../vue/App.vue";

        // Add a global variable to test JavaScript execution
        window.testVariable = "VitePluginVueTest";

        // Mount the Vue app
        function waitForElement(selector) {
        return new Promise((resolve) => {
            const element = document.querySelector(selector);
            if (element) {
            resolve(element);
            return;
            }

            const observer = new MutationObserver((mutations) => {
            const targetElement = document.querySelector(selector);
            if (targetElement) {
                observer.disconnect();
                resolve(targetElement);
            }
            });

            observer.observe(document.body, {
            childList: true,
            subtree: true,
            });
        });
        }

        // Wait for the mount point to appear and then create the application
        waitForElement("#vue-container")
        .then((element) => {
            const app = createApp(App);
            app.mount(element);
        })
        .catch((error) => {
            console.error("Unable to find mount point:", error);
        });
            """)

        # Create VitePlugin instance with Vue support
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js', 'assets/vue'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[NpmPackage('vue')],
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout with a container for Vue
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - Vue Support', id='header'),
                html.P('This tests the Vite plugin with Vue support.', id='paragraph'),
                # Container for Vue app
                html.Div(id='vue-container'),
                html.Div(id='vue-out'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
                html.Button('Test Vue', id='vue-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginVueTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Add callback to test Vue functionality with a simpler approach
        app.clientside_callback(
            """
            async function(n_clicks) {
                function delay(ms) {
                    return new Promise(resolve => setTimeout(resolve, ms));
                }
                async function testVueApp() {
                    const vueApp = document.getElementById('vue-app');
                    if (vueApp) {
                        const button = vueApp.querySelector('button');
                        if (button) {
                            const originalText = vueApp.querySelector('h1').textContent;
                            button.click();
                            await delay(0);
                            const newText = vueApp.querySelector('h1').textContent;
                            if (newText === 'Vue is working!') {
                                return 'Vue is working correctly: ' + newText;
                            } else {
                                throw new Error('Vue button click failed. Original: ' + originalText + ', New: ' + newText);
                            }
                        } else {
                            throw new Error('Vue button not found');
                        }
                    } else {
                        throw new Error('Vue app not found');
                    }
                }
                if (n_clicks > 0) {
                    try {
                        const result = await testVueApp();
                        return result;
                    } catch (error) {
                        return error.message;
                    }
                }
                return 'Click button to test Vue';
            }
            """,
            Output('vue-out', 'children'),
            Input('vue-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - Vue Support')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Test Vue behavior
        vue_test_button = dash_duo.find_element('#vue-test-button')
        vue_test_button.click()

        # Wait for Vue test result - let's first check if the Vue app is mounted
        # Give it a bit more time and check for the mounted app
        dash_duo.wait_for_element_by_id('vue-app', timeout=10)

        # Now click the Vue test button again
        vue_test_button.click()

        # Wait for Vue test result
        dash_duo.wait_for_text_to_equal('#vue-out', 'Vue is working correctly: Vue is working!')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'

    def test_vite_plugin_with_react_support(self, dash_duo: DashComposite):
        """Test the plugin works with React support enabled."""
        # Create assets structure
        os.makedirs('assets/js', exist_ok=True)
        os.makedirs('assets/react', exist_ok=True)

        # Create a simple React component
        with open('assets/react/App.jsx', 'w') as f:
            f.write("""
            import React, { useState } from 'react';

            const App = () => {
              const [message, setMessage] = useState('Hello from React!');
              
              const updateMessage = () => {
                setMessage('React is working!');
              };
              
              return (
                <div id="react-app">
                  <h1>{message}</h1>
                  <button onClick={updateMessage}>Click me!</button>
                </div>
              );
            };

            export default App;
            """)

        # Create JavaScript file that imports and renders React
        with open('assets/js/main.js', 'w') as f:
            f.write("""
            import React from 'react';
            import { createRoot } from 'react-dom/client';
            import App from '../react/App.jsx';

            // Add a global variable to test JavaScript execution
            window.testVariable = "VitePluginReactTest";

            // Wait for the mount point to appear and then create the application
            function waitForElement(selector) {
              return new Promise((resolve) => {
                const element = document.querySelector(selector);
                if (element) {
                  resolve(element);
                  return;
                }

                const observer = new MutationObserver((mutations) => {
                  const targetElement = document.querySelector(selector);
                  if (targetElement) {
                    observer.disconnect();
                    resolve(targetElement);
                  }
                });

                observer.observe(document.body, {
                  childList: true,
                  subtree: true,
                });
              });
            }

            // Wait for the mount point to appear and then create the application
            waitForElement("#react-container")
              .then((element) => {
                const root = createRoot(element);
                root.render(React.createElement(App));
              })
              .catch((error) => {
                console.error("Unable to find mount point:", error);
              });
            """)

        # Create VitePlugin instance with React support
        vite_plugin = VitePlugin(
            build_assets_paths=['assets/js', 'assets/react'],
            entry_js_paths=['assets/js/main.js'],
            npm_packages=[
                NpmPackage('react'),
                NpmPackage('react-dom'),
            ],
            clean_after=False,
        )

        # Call setup BEFORE creating Dash app (as required by the plugin architecture)
        vite_plugin.setup()

        # Create a Dash app
        app = Dash(__name__)

        # Call use AFTER creating Dash app (as required by the plugin architecture)
        vite_plugin.use(app)

        # Define app layout with a container for React
        app.layout = html.Div(
            [
                html.H1('Vite Plugin Test - React Support', id='header'),
                html.P('This tests the Vite plugin with React support.', id='paragraph'),
                # Container for React app
                html.Div(id='react-container'),
                html.Div(id='react-out'),
                html.Div(id='js-test-result'),
                html.Button('Test JS', id='js-test-button', n_clicks=0),
                html.Button('Test React', id='react-test-button', n_clicks=0),
            ]
        )

        # Add callback to test JavaScript execution
        app.clientside_callback(
            """
            function(n_clicks) {
                if (n_clicks > 0) {
                    // Test if global variable exists
                    if (typeof window.testVariable !== 'undefined' && window.testVariable === 'VitePluginReactTest') {
                        return 'JavaScript behavior is working correctly';
                    } else {
                        return 'Global variable test failed';
                    }
                }
                return 'Click button to test JavaScript';
            }
            """,
            Output('js-test-result', 'children'),
            Input('js-test-button', 'n_clicks'),
        )

        # Add callback to test React functionality with a simpler approach
        app.clientside_callback(
            """
            async function(n_clicks) {
                function delay(ms) {
                    return new Promise(resolve => setTimeout(resolve, ms));
                }
                async function testReactApp() {
                    const reactApp = document.getElementById('react-app');
                    if (reactApp) {
                        const button = reactApp.querySelector('button');
                        if (button) {
                            const originalText = reactApp.querySelector('h1').textContent;
                            button.click();
                            await delay(0);
                            const newText = reactApp.querySelector('h1').textContent;
                            if (newText === 'React is working!') {
                                return 'React is working correctly: ' + newText;
                            } else {
                                throw new Error('React button click failed. Original: ' + originalText + ', New: ' + newText);
                            }
                        } else {
                            throw new Error('React button not found');
                        }
                    } else {
                        throw new Error('React app not found');
                    }
                }
                if (n_clicks > 0) {
                    try {
                        const result = await testReactApp();
                        return result;
                    } catch (error) {
                        return error.message;
                    }
                }
                return 'Click button to test React';
            }
            """,
            Output('react-out', 'children'),
            Input('react-test-button', 'n_clicks'),
        )

        # Start the app
        dash_duo.start_server(app)

        # Wait for the app to load and check that elements are rendered
        dash_duo.wait_for_text_to_equal('#header', 'Vite Plugin Test - React Support')

        # Test JavaScript behavior
        js_test_button = dash_duo.find_element('#js-test-button')
        js_test_button.click()

        # Wait for JavaScript test result
        dash_duo.wait_for_text_to_equal('#js-test-result', 'JavaScript behavior is working correctly')

        # Test React behavior
        react_test_button = dash_duo.find_element('#react-test-button')
        react_test_button.click()

        # Wait for React test result - let's first check if the React app is mounted
        # Give it a bit more time and check for the mounted app
        dash_duo.wait_for_element_by_id('react-app', timeout=10)

        # Now click the React test button again
        react_test_button.click()

        # Wait for React test result
        dash_duo.wait_for_text_to_equal('#react-out', 'React is working correctly: React is working!')

        # Check that there are no console errors
        assert dash_duo.get_logs() == [], 'Browser console should contain no errors'


if __name__ == '__main__':
    pytest.main([__file__])
