import React from "react";
import { createRoot } from "react-dom/client";
import LightningComponent from "./react_components/Lightning.jsx";

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    renderBackground: (timeoutCount, id) => {
      const container = document.getElementById(id);
      const root = createRoot(container);
      root.render(React.createElement(LightningComponent));

      return window.dash_clientside.no_update;
    },
  },
});
