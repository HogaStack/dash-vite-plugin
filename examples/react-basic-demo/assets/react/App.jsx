import React, { useState } from 'react';

const App = () => {
    const [message, setMessage] = useState("Hello from React!");

    const updateDash = () => {
        setMessage("Hello from React!");
        window.dash_clientside.set_props('dash-title', { children: 'Hello from React!' });
    };

    const updateMessage = () => {
        setMessage("Hello from Dash!");
    };

    return (
        <div id="react-app" style={{ margin: "20px" }}>
            <h1 style={{ color: "#42b883" }}>{message}</h1>
            <div>
                <button id="control-dash-button" onClick={updateDash}>Control Dash</button>
            </div>
            <div hidden>
                <button id="control-react-button" onClick={updateMessage}>Control Vue</button>
            </div>
        </div>
    );
};

export default App;