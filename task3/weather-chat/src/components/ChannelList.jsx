import React, { useEffect, useState } from "react";
import { fetchChannels } from "../api";

export default function ChannelList({ onSelectChannel }) {
    const [channels, setChannels] = useState([]);

    useEffect(() => {
        console.log("Fetching channels..."); // Debugging

        fetchChannels()
            .then((data) => {
                console.log("Fetched channels:", data); // Debugging
                setChannels(data.channels);
            })
            .catch((error) => console.error("Error fetching channels:", error));
    }, []);

    return (
        <div>
            <h2>Available Channels</h2>
            <ul>
                {channels.length === 0 ? (
                    <p>No channels found</p>
                ) : (
                    channels.map((channel) => (
                        <li key={channel.endpoint}>
                            <button onClick={() => onSelectChannel(channel)}>
                                {channel.name}
                            </button>
                        </li>
                    ))
                )}
            </ul>
        </div>
    );
}
