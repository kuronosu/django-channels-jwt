import "./App.css";
import React, { useEffect, useState } from "react";
import useEventWebSocket, { getConnectionStatus } from "./useEventWebSocket";

// ws://127.0.0.1:8000/ws/chat/asd/

function App() {
  const [user, setUser] = useState("kuro");
  const [token, setToken] = useState(null);

  const [room, setRoom] = useState("asd");

  const [socketUrl, setSocketUrl] = useState(null);
  const { readyState, sendEvent, onEvent } = useEventWebSocket(socketUrl);

  useEffect(() => {
    if (
      room !== null &&
      room.trim().length > 0 &&
      token !== null &&
      token.trim().length > 0
    ) {
      setSocketUrl(`ws://127.0.0.1:8000/ws/chat/${room}/?token=${token}`);
    }
  }, [room, token]);

  return (
    <div className="App">
      <h1>{getConnectionStatus(readyState)}</h1>
      {token ? (
        <Chat sendEvent={sendEvent} room={room} onEvent={onEvent} />
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetch("http://127.0.0.1:8000/api/token/", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                username: user,
                password: user,
              }),
            })
              .then((res) => res.json())
              .then((data) => {
                setToken(data.access);
              })
              .catch((err) => {
                console.error(err);
              });
          }}
        >
          <input
            required
            type="text"
            value={user}
            placeholder="User"
            onChange={(e) => setUser(e.target.value)}
          />
          <input
            required
            type="text"
            value={room}
            placeholder="Room"
            onChange={(e) => setRoom(e.target.value)}
          />
          <br />
          <button type="submit">Enviar</button>
        </form>
      )}
    </div>
  );
}

export default App;

function Chat({ sendEvent, room, onEvent }) {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  useEffect(() => {
    console.log("Listening for event chat:new_message");
    onEvent("chat:new_message", (payload) => {
      setMessages((prev) => prev.concat(payload));
    });
  }, [onEvent]);
  return (
    <div>
      <h1>Chat {room}</h1>
      <ul>
        {messages.map(({ user, message }, idx) => (
          <ChatMessage key={idx} user={user} message={message} />
        ))}
      </ul>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendEvent("message", message);
          setMessage("");
        }}
      >
        <input
          type="text"
          value={message}
          placeholder="Message"
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit">Enviar</button>
      </form>
    </div>
  );
}

function ChatMessage({ user, message }) {
  return (
    <li>
      {user}: {message}
    </li>
  );
}
