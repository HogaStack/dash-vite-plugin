import os
from dash import Dash, html, Input, Output
from dash_vite_plugin import VitePlugin, NpmPackage


# Create assets structure
os.makedirs('assets/js', exist_ok=True)
os.makedirs('assets/vue', exist_ok=True)

# Create a simple Vue component using Vue 3 Composition API
with open('assets/vue/App.vue', 'w') as f:
    f.write("""<template>
  <div id="vue-app">
    <h1>{{ message }}</h1>
    <div>
      <button id="control-dash-button" @click="updateDash">Control Dash</button>
    </div>
    <div hidden>
      <button id="control-vue-button" @click="updateMessage">Control Vue</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const message = ref("Hello from Vue!");

const updateDash = () => {
  message.value = "Hello from Vue!";
  window.dash_clientside.set_props('dash-title', { children: 'Hello from Vue!' });
};

const updateMessage = () => {
  message.value = "Hello from Dash!";
};
</script>

<style scoped>
#vue-app {
  margin: 20px;
}
h1 {
  color: #42b883;
}
</style>
    """)

# Create JavaScript file that imports and mounts Vue
with open('assets/js/main.js', 'w') as f:
    f.write("""import { createApp } from "vue";
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
    npm_packages=[
        NpmPackage('vue'),
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
