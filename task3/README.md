# Weather Chat
**Task 3 Submission for AI and the Web**  

This project implements a **distributed message board channel** named **Weather Chat**, deployed on the university server. It includes:
- A **Flask-based channel server** (`channel.py`) that manages messages and integrates with a **weather API**.
- A **React-based client** (`weather-chat`) that provides an improved chat interface using npm.
- **A local hub instance (`hub.py`)** to manage channels.
- **Deployment on an Apache server** following the university setup.

---

## Task Completion Summary  

### **1️ Channel Server**
- **Channel Name & Topic**  
  - **Name:** *Weather Chat*  
  - **Topic:** Discuss the weather and get real-time weather updates.
  - **Welcome Message:** First message in the chat explains the channel’s purpose.

- **Message Limitation**  
  - Stores only the **latest 99 messages** to avoid excessive storage.

- **Message Filtering**  
  - **Profanity filter** prevents offensive words in both messages and usernames. (using the better_profanity library)

- **Active Responses**  
  - The bot **automatically detects city names** in user messages and provides live weather data.  
  - Uses **Open-Meteo API** for real-time weather updates.  
  - Humorously suggests weather updates with messages like:  
    *"My neural circuits just had a hunch... You need to know the weather!"*

- **Deployment**  
  - Hosted on the **university server** and registered with a seperate hub instance (huge issues getting it on the public hub for some reason).
  - **Accessible via:**  
    - `http://vm146.rz.uni-osnabrueck.de/~u045/channel.wsgi/`

---

### **React Client**
- **Replaces Flask Client**  
  - Implements all functionality of the basic Flask client.
  - **Cleaner UI** with improved styling and layout.

- **Fancier Design & Extra Features**
  - **Chat Bubbles** with clear sender identification and timestamps.
  - **Username Persistence** (saved locally in the browser).
  - **Auto-scrolling** to the latest messages.
  - **Profanity check for usernames** before allowing a user to join.

- **Deployment on University Server**  
  - **Client is fully deployed** and available at:  
    - `http://vm146.rz.uni-osnabrueck.de/~u045/weather-chat/`
  - **Integrated with own hub instance**, not the public hub.

---

## Running the Project Locally  

```sh
git clone https://github.com/lleisner/web_ai.git
cd web_ai/task3

# Optional, activate virtual env. E.g.:
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python hub.py
python channel.py

flask --app channel.py register
cd weather-chat
npm install
npm run dev