import dash
from dash import html
from dash.dependencies import Input, Output
from dash_vite_plugin import VitePlugin, NpmPackage

# Create VitePlugin instance with Vue support
vite_plugin = VitePlugin(
    build_assets_paths=['assets/js', 'assets/vue'],
    entry_js_paths=['assets/js/main.js'],
    npm_packages=[
        NpmPackage('vue'),
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

# Define app layout with a container for Vue
app.layout = html.Div(
    [
        html.H1('Vite Plugin Test - Vue Support', id='header'),
        html.P('This tests the Vite plugin with Vue support.', id='paragraph'),
        # Container for Vue app
        html.Div(
            [
                'The content from Vue',
                html.Div(id='vue-container'),
            ]
        ),
        html.Div(
            [
                'The content from Dash',
                html.Div(
                    [html.H1('Hello from Dash!', id='dash-title'), html.Button('Control Vue', id='dash-button')],
                    id='dash-app',
                    style={'margin': '20px'},
                ),
            ],
            id='dash-container',
        ),
    ]
)


# Add callback to test Vue functionality with a simpler approach
app.clientside_callback(
    """
    function(n_clicks) {
      if (n_clicks > 0) {
        const vueApp = document.getElementById('vue-app');
        if (vueApp) {
            const button = vueApp.querySelector('#control-vue-button');
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
