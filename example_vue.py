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
    <button @click="updateMessage">Click me!</button>
  </div>
</template>

<script setup>
import { ref } from "vue";

const message = ref("Hello from Vue!");

const updateMessage = () => {
  message.value = "Vue is working!";
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
        NpmPackage('vue'),  # Removed version to use default/latest
    ],
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


if __name__ == '__main__':
    app.run(debug=True)
