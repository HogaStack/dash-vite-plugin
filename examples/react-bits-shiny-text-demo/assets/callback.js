import React from "react";
import { createRoot } from "react-dom/client";
import ShinyTextComponent from "./react_components/ShinyText.jsx";

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    renderText: (timeoutCount, id) => {
      const container = document.getElementById(id);
      const root = createRoot(container);
      root.render(React.createElement(ShinyTextComponent));

      return window.dash_clientside.no_update;
    },
  },
});
