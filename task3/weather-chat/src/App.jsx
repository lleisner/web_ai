import React, { useState } from "react";
import ChannelList from "./components/ChannelList";
import ChatWindow from "./components/ChatWindow";

export default function App() {
    const [selectedChannel, setSelectedChannel] = useState(null);

    return (
        <div>
            <h1>Weather Chat</h1>
            {!selectedChannel ? (
                <ChannelList onSelectChannel={setSelectedChannel} />
            ) : (
                <ChatWindow channel={selectedChannel} onBack={() => setSelectedChannel(null)} />
            )}
        </div>
    );
}
