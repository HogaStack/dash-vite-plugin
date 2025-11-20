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

  const updateDash = () => {
    setMessage("Hello from React!");
    window.dash_clientside.set_props('dash-title', { children: 'Hello from React!' });
  };

  const updateMessage = () => {
    setMessage("Hello from Dash!");
  };

  return (
    <div id="react-app" style={{ margin: "20px" }}>
      <h1 style={{ color: "#42b883" }}>{message}</h1>
      <div>
        <button id="control-dash-button" onClick={updateDash}>Control Dash</button>
      </div>
      <div hidden>
        <button id="control-react-button" onClick={updateMessage}>Control Vue</button>
      </div>
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
    download_node=True,
    clean_after=True,
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
        html.Div(
            [
                'The content from React',
                html.Div(id='react-container'),
            ]
        ),
        html.Div(
            [
                'The content from Dash',
                html.Div(
                    [html.H1('Hello from Dash!', id='dash-title'), html.Button('Control React', id='dash-button')],
                    id='dash-app',
                    style={'margin': '20px'},
                ),
            ],
            id='dash-container',
        ),
    ]
)


# Add callback to test React functionality with a simpler approach
app.clientside_callback(
    """
    function(n_clicks) {
      if (n_clicks > 0) {
        const reactApp = document.getElementById('react-app');
        if (reactApp) {
            const button = reactApp.querySelector('#control-react-button');
            if (button) {
                button.click();
                return 'Hello from Dash!';
            }
        }
      }
      return 'Hello from Dash!';
    }
    """,
    Output('dash-title', 'children'),
    Input('dash-button', 'n_clicks'),
)


if __name__ == '__main__':
    app.run(debug=True)
