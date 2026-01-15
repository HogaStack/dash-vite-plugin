import React from "react";
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
