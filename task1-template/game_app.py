import streamlit as st
from guessing_game import GuessingGame
from stats_manager import StatsManager


class GameApp:
    def __init__(self, api_key):
        """
        Initialize the GameApp with GuessingGame and Streamlit state management.
        """
        self.game = GuessingGame(api_key)
        self.stats_manager = StatsManager()

        # Initialize session state for chat history and game over status
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "show_hints" not in st.session_state:
            st.session_state.show_hints = False
            
        if "used_animals" not in st.session_state:
            st.session_state.used_animals = set()
            
        if "show_solution" not in st.session_state:
            st.session_state.show_solution = False
            
        if "game_over" not in st.session_state:
            st.session_state.game_over = False
        
        if "game_stats" not in st.session_state:
            st.session_state.game_stats = []

    def run(self):
        """
        Render the Streamlit UI and manage the navigation between pages.
        """
        st.title("🌍🦁 Wild Guess 🐾❓")

        # Sidebar for page navigation
        page = st.sidebar.radio("Navigate", ["Play", "Stats"])

        # Navigate between Play and Stats pages
        if page == "Play":
            self.play_game()
        elif page == "Stats":
            self.show_stats()            

    def reset_game(self):
        """
        Reset the game for a new session and clear the Streamlit state.
        """
        self.game.reset_game()
        st.session_state.chat_history = []
        st.session_state.show_hints = False
        st.session_state.game_over = False
        st.session_state.show_solution = False
        
    def save_stats(self):    
        # Calculate stats for this game
        num_guesses = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
        total_relevance_score = sum(
            int(msg["content"].split(":")[1].strip()) for msg in st.session_state.chat_history
            if msg["role"] == "assistant" and msg.get("type") == "relevance_score"
        )
        avg_relevance_score = total_relevance_score / max(1, num_guesses) # Prevent division by zero
        
        # Log stats using StatsManager
        self.stats_manager.add_game_stats(
            target_animal=self.game.target_animal,
            num_guesses=num_guesses,
            avg_relevance_score=avg_relevance_score
        )

        # Update session stats
        st.session_state.game_stats.append({
            "num_guesses": num_guesses,
            "avg_relevance_score": avg_relevance_score,
            "target_animal": self.game.target_animal,
        })

    def play_game(self):
        """
        Render the Streamlit UI and manage the game loop.
        """
        st.header("🎮 Guess the Animal!")

        # Always provide the "Start a New Game" button
        if st.button("Start a New Game"):
            self.reset_game()
            
        # Display hints if the user clicks "Get Hints"
        if st.button("Get Hints"):
            st.session_state.show_hints = not st.session_state.show_hints
        
        if st.session_state.show_hints:
            known_facts = self.game.get_known_facts()
            st.subheader("Known Facts")
            st.write(known_facts)
            
        if st.button("Show Solution"):
            solution = self.game.target_animal
            st.subheader("Target Animal")
            st.write(solution)
            st.session_state.game_over = True
            
        # Check if the game is over
        if st.session_state.game_over:
            self.handle_game_over()
            if self.game.game_over:
                self.save_stats()
        else:
            self.display_interaction()
            

    def submit_question(self, user_input):
        """
        Process the user's question and update Streamlit state.

        Args:
            user_input (str): The user's question.

        Returns:
            None
        """
        # Process the question using GuessingGame
        response = self.game.process_question(user_input)

        # Update the chat history in Streamlit session state
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "type": "response", "content": response["response"]})
        st.session_state.chat_history.append({"role": "assistant", "type": "relevance_score", "content": response["relevance_score"]})
       
        # Update the game_over state if the game is finished
        st.session_state.game_over = self.game.game_over


    def handle_game_over(self, cheat=False):
        """
        Handle the game-over state by displaying the full conversation history
        and providing a recap.
        """
        st.success("🎉 You've guessed the animal correctly!")
        st.subheader("Full Conversation History")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            elif message["role"] == "assistant":
                st.write(f"**Assistant:** {message['content']}")
                
    def display_interaction(self):
        """
        Display the most recent interaction and manage the game play input.
        """
        st.subheader("Current Interaction")

        # Display the latest user question
        if st.session_state.chat_history:
            last_user_message = next(
                (msg["content"] for msg in reversed(st.session_state.chat_history) if msg["role"] == "user"), None
            )
            if last_user_message:
                st.write(f"**You:** {last_user_message}")

            # Display the latest assistant response
            last_assistant_message = next(
                (msg["content"] for msg in reversed(st.session_state.chat_history) if msg["role"] == "assistant" and msg.get("type") == "response"), None
            )
            if last_assistant_message:
                st.write(f"**Assistant:** {last_assistant_message}")
                
            # Display the comment about the relevance score
            last_comment = next(
                (msg["content"] for msg in reversed(st.session_state.chat_history) if msg["role"] == "assistant" and msg.get("type") == "relevance_score"), None
            )
            if last_comment:
                st.write(f"**Comment:** {last_comment}")

        # Game Play
        def process_input():
            user_input = st.session_state["user_input"]
            if user_input:
                self.submit_question(user_input)
                # Clear the input field
                st.session_state["user_input"] = ""

        # Add the text input with a callback
        st.text_input("Ask a question:", key="user_input", on_change=process_input)

    def show_stats(self):
        """
        Display the stats page using Streamlit's built-in charting tools.
        """
        st.header("📊 Game Statistics")

        # Combine session stats and all-time stats
        combined_stats = self.stats_manager.get_combined_stats()
        if not combined_stats:
            st.info("No game data available. Play some games first!")
            return

        # Extract data for visualization
        game_indices = [i + 1 for i in range(len(combined_stats))]
        num_guesses = [game["num_guesses"] for game in combined_stats]
        avg_relevance_scores = [game["avg_relevance_score"] for game in combined_stats]


        st.subheader("Performance over all games")
        st.line_chart({"Number of Guesses": num_guesses, "Avg Relevance Score": avg_relevance_scores})

        # Display summary statistics
        summary = self.stats_manager.get_summary()
        st.subheader("Summary")
        st.write(f"**Total Games Played**: {summary['total_games']}")
        st.write(f"**Average Number of Guesses**: {summary['avg_guesses']:.2f}")
        st.write(f"**Overall Avg Relevance Score**: {summary['avg_relevance_score']:.2f}")
