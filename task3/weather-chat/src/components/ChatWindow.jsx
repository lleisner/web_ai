import React, { useEffect, useState, useRef } from "react";
import { fetchMessages, postMessage } from "../api";
import "../styles.css";

export default function ChatWindow({ channel, onBack }) {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState("");
    const [username, setUsername] = useState(localStorage.getItem("username") || "");
    const [isUsernameSet, setIsUsernameSet] = useState(!!username);
    const [errorMessage, setErrorMessage] = useState("");

    const messageEndRef = useRef(null); // Reference for auto-scrolling to bottom of chat

    useEffect(() => {
        async function loadMessages() {
            try {
                const data = await fetchMessages(channel.endpoint, channel.authkey);
                setMessages(data);
            } catch (error) {
                console.error("Error fetching messages:", error);
            }
        }

        loadMessages();
        const interval = setInterval(loadMessages, 3000);
        return () => clearInterval(interval);
    }, [channel]);

    // Auto-scroll on message update
    useEffect(() => {
        messageEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    async function sendMessage() {
        if (!newMessage.trim() || !isUsernameSet) return;
    
        try {
            const data = await postMessage(channel.endpoint, channel.authkey, newMessage, username);
    
            if (data.status === "blocked") {
                setErrorMessage(data.error); // Show profanity warning in UI
            } else if (data.status === "error") {
                setErrorMessage(" Error: " + data.error);
            } else {
                setNewMessage("");
                setErrorMessage(""); // Clear error if message is valid
                fetchMessages(channel.endpoint, channel.authkey).then(setMessages);
            }
        } catch (error) {
            console.error("Error sending message:", error);
            setErrorMessage("Something went wrong. Try again.");
        }
    }

    function formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }); // Format: HH:MM AM/PM
    }
    
    function handleInputChange(event) {
        setNewMessage(event.target.value);
        setErrorMessage(""); // Reset error message when typing
    }

    function handleKeyPress(event) {
        if (event.key === "Enter" && !event.shiftKey) { 
            event.preventDefault(); // Prevents line breaks in the input field
            sendMessage();
        }
    }
    

    async function confirmUsername() {
        if (!username.trim()) return;

        // Check if username contains profanity
        const response = await fetch("http://localhost:5001/check_profanity", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: username }),
        });

        const data = await response.json();
        if (data.is_profane) {
            setErrorMessage("Please choose a different username.");
            return;
        }

        localStorage.setItem("username", username);
        setIsUsernameSet(true);
    }

    function resetUsername() {
        localStorage.removeItem("username");
        setUsername("");
        setIsUsernameSet(false);
        setErrorMessage("");
    }

    function handleUsernameChange(event) {
        setUsername(event.target.value);
        setErrorMessage(""); // Reset error message when typing
    }

    return (
        <div className="chat-container">
            <button onClick={onBack}>← Back to Channels</button>
            <h2>Chat - {channel.name}</h2>

            {!isUsernameSet ? (
                <div className="username-container">
                    <label>Enter Username: </label>
                    <input
                        type="text"
                        value={username}
                        onChange={handleUsernameChange}
                        placeholder="Your name"
                    />
                    <button onClick={confirmUsername}>Set Username</button>
                    {errorMessage && <p className="error">{errorMessage}</p>} {/* Show error if username is bad */}
                </div>
            ) : (
                <div className="username-container">
                    <p>Logged in as: <strong>{username}</strong></p>
                    <button onClick={resetUsername}>Change Username</button>
                </div>
            )}

            <div className="chat-window">
                <ul className="message-list">
                    {messages.map((msg, index) => (
                        <li key={index} className={`message ${msg.sender === username ? "user" : "bot"}`}>
                            <div className="message-header">
                                <strong>{msg.sender}</strong>
                                <span className="timestamp">{formatTimestamp(msg.timestamp)}</span>
                            </div>
                            <p>{msg.content}</p>
                        </li>
                    ))}
                    <div ref={messageEndRef} />
                </ul>


                {errorMessage && <p className="error">{errorMessage}</p>} {/* Show profanity errors */}

                <div className="input-container">
                    <input
                        type="text"
                        value={newMessage}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyPress}
                        placeholder="Type a message..."
                        disabled={!isUsernameSet}
                    />
                    <button onClick={sendMessage} disabled={!isUsernameSet || !newMessage.trim()}>
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
