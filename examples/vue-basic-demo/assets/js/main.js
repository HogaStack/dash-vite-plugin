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
