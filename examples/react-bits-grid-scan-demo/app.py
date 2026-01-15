import dash
from dash import html
import feffery_utils_components as fuc
from dash_vite_plugin import VitePlugin, NpmPackage
from dash.dependencies import Input, State, ClientsideFunction

vite_plugin = VitePlugin(
    build_assets_paths=['assets'],
    entry_js_paths=['assets/callback.js'],
    npm_packages=[
        NpmPackage('react'),
        NpmPackage('react-dom'),
        NpmPackage('three'),
        NpmPackage('postprocessing'),
        NpmPackage('face-api.js'),
    ],
    download_node=True,
    clean_after=False,  # 开发阶段建议设置为False以加速构建
)

vite_plugin.setup()

app = dash.Dash(__name__)

vite_plugin.use(app)

app.layout = html.Div(
    [
        fuc.FefferyTimeout(id='trigger-background-init', delay=100),
        html.Div(id='background-mount'),
    ]
)

app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='renderBackground'),
    Input('trigger-background-init', 'timeoutCount'),
    State('background-mount', 'id'),
)

if __name__ == '__main__':
    app.run(debug=True)
