import dash
from dash import html
from dash.dependencies import Input, Output
from dash_vite_plugin import VitePlugin, NpmPackage

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
app = dash.Dash(__name__)

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
