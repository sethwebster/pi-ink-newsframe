import React from "react";
import sendCommand from "./api";
import "./App.css";
import Layout from "./containers/Layout";

const buttons = [
  { text: "Next", command: "NEXT" },
  { text: "Update", command: "UPDATE" },
  { text: "Restart", command: "RESTART" },
  { text: "Shutdown", command: "SHUTDOWN" },
];

function App() {
  const handleClick = (command: string, args: string[]) => {
    sendCommand(command, args).then((res) => console.log(res));
  };

  return (
    <Layout>
      <div className="flex w-full flex-col">
        <div
          id="header"
          className="w-full bg-blue-500 text-center shadow-md h-16 text-lg"
        >
          <h2 className="font-bold mt-4 text-white">NewsFrame Commander</h2>
        </div>
        <div id="actions" className="w-32 ml-auto mr-auto">
          {buttons.map((button) => (
            <button
              key={button.command}
              className="bg-blue-800 p-3 min-w-full w-full shadow-md rounded-md hover:bg-blue-500"
              onClick={() => handleClick(button.command, [])}
            >
              {button.text}
            </button>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default App;
