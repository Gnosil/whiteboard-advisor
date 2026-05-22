import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import ShareView from "./ShareView";
import "./index.css";

const shareToken = new URLSearchParams(location.search).get("share");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {shareToken ? <ShareView token={shareToken} /> : <App />}
  </React.StrictMode>
);
