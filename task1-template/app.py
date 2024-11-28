import streamlit as st
#from utils import load_api_key
from game_app import GameApp

@st.cache_resource
def intialize_app(_api_key):
    return GameApp(_api_key)

#api_key = load_api_key()
api_key = "Your api key here"
app = intialize_app(api_key)
app.run()