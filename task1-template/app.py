import streamlit as st

st.title("Guessing Game")
st.header("Welcome")
st.write("This is a guessing game")

guess = st.text_input("Enter your guess:")
submit_button = st.button("Submit")

if "game_state" not in st.session_state:
    st.session_state["game_state"] = {
        "target": 42, 
        "attempts": 0
    }
    
st.write(f"Attempts {st.session_state["game_state"]["attempts"]}")

if st.button("Guess"):
    st.session_state["game_state"]["attempts"] += 1
    
page = st.sidebar.selectbox("Choose a page", ["Play", "Stats"])

if page == "Play":
    st.title("Play Page")
    st.write("Welcome to the guessing game!")
elif page == "Stats":
    st.title("Stats Page")
    st.write("Here are your stats.")