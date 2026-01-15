import dash
from dash import html
import feffery_antd_components as fac
import feffery_utils_components as fuc
from feffery_dash_utils.style_utils import style
from dash_vite_plugin import VitePlugin, NpmPackage
from dash.dependencies import Input, State, ClientsideFunction


vite_plugin = VitePlugin(
    build_assets_paths=['assets'],
    entry_js_paths=['assets/callback.js'],
    npm_packages=[
        NpmPackage('react'),
        NpmPackage('react-dom'),
        NpmPackage('motion'),
    ],
    download_node=True,
    clean_after=False,  # 开发阶段建议设置为False以加速构建
)

vite_plugin.setup()

app = dash.Dash(__name__)

vite_plugin.use(app)

app.layout = html.Div(
    [
        fuc.FefferyTimeout(id='trigger-text-init', delay=100),
        fac.AntdCenter(
            id='text-mount',
            style=style(
                position='fixed',
                width='100vw',
                height='100vh',
                left=0,
                top=0,
                background='#060010',
                fontSize=56,
            ),
        ),
    ]
)

app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='renderText'),
    Input('trigger-text-init', 'timeoutCount'),
    State('text-mount', 'id'),
)

if __name__ == '__main__':
    app.run(debug=True)
