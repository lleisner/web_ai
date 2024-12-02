import streamlit as st
from game_app import GameApp

@st.cache_resource
def intialize_app(_api_key):
    return GameApp(_api_key)

api_key = st.secrets["openai_api_key"]

app = intialize_app(api_key)
app.run()