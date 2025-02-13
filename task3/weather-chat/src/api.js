// Dynamically determine the backend URL based on the environment
const LOCAL_URL = "http://localhost:5001";
const SERVER_URL = "http://vm146.rz.uni-osnabrueck.de/u045/channel.wsgi";
const BASE_URL = window.location.hostname === "localhost" ? LOCAL_URL : SERVER_URL;

// Hub URL (for fetching available channels)
const HUB_URL = "http://localhost:5555";

/**
 * Fetch all channels from the hub
 */
export async function fetchChannels() {
    const response = await fetch(`${HUB_URL}/channels`);
    if (!response.ok) throw new Error("Error fetching channels");
    return response.json();
}

/**
 * Fetch messages for a specific channel
 */
export async function fetchMessages(channelEndpoint, authKey) {
    const response = await fetch(channelEndpoint, {
        headers: { Authorization: `authkey ${authKey}` },
    });

    if (!response.ok) {
        throw new Error("Error fetching messages");
    }

    return response.json();
}

/**
 * Post a new message to a channel
 */
export async function postMessage(endpoint, authkey, content, sender) {
    const response = await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `authkey ${authkey}`
        },
        body: JSON.stringify({
            content,
            sender,
            timestamp: new Date().toISOString(),
        })
    });

    // Check if response is JSON before parsing
    const text = await response.text();
    try {
        return JSON.parse(text);
    } catch (error) {
        console.error("Failed to parse response as JSON:", text);
        return { status: "error", error: "Unexpected response from server" };
    }
}
