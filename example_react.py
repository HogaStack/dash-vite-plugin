import os
from dash import Dash, html, Input, Output
from dash_vite_plugin import VitePlugin, NpmPackage


# Create assets structure
os.makedirs('assets/js', exist_ok=True)
os.makedirs('assets/react', exist_ok=True)

# Create a simple React component
with open('assets/react/App.jsx', 'w') as f:
    f.write("""import React, { useState } from 'react';

const App = () => {
  const [message, setMessage] = useState("Hello from React!");

  const updateMessage = () => {
    setMessage("React is working!");
  };

  return (
    <div id="react-app" style={{ margin: "20px" }}>
      <h1 style={{ color: "#42b883" }}>{message}</h1>
      <button onClick={updateMessage}>Click me!</button>
    </div>
  );
};

export default App;
    """)

# Create JavaScript file that imports and renders React
with open('assets/js/main.js', 'w') as f:
    f.write("""import React from "react";
import { createRoot } from "react-dom/client";
import App from "../react/App.jsx";

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


if __name__ == '__main__':
    app.run(debug=True)
