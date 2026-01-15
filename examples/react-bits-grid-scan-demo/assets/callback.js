import React from "react";
import { createRoot } from "react-dom/client";
import GridScanComponent from "./react_components/GridScan.jsx";

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    renderBackground: (timeoutCount, id) => {
      const container = document.getElementById(id);
      const root = createRoot(container);
      root.render(React.createElement(GridScanComponent));

      return window.dash_clientside.no_update;
    },
  },
});
