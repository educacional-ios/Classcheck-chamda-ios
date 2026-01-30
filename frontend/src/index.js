import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  // <React.StrictMode> // Temporariamente desabilitado para debug dos erros DOM
  <App />
  // </React.StrictMode>
);
