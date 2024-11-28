import json

class StatsManager:
    def __init__(self, stats_file="game_stats.json"):
        """
        Initialize the StatsManager.

        Args:
            stats_file (str): Path to the file for storing all-time stats.
        """
        self.stats_file = stats_file
        self.session_stats = []  # List to store stats for the current session

    def add_game_stats(self, target_animal, num_guesses, avg_relevance_score):
        """
        Add stats for a completed game to the session and save them to all-time storage.

        Args:
            target_animal (str): The target animal for the game.
            num_guesses (int): Number of guesses in the game.
            avg_relevance_score (float): Average relevance score across all questions.
        """
        game_stats = {
            "target_animal": target_animal,
            "num_guesses": num_guesses,
            "avg_relevance_score": avg_relevance_score,
        }

        # Add to session stats
        self.session_stats.append(game_stats)

        # Save to persistent storage
        self._save_to_file(game_stats)

    def get_combined_stats(self):
        """
        Combine session stats with all-time stats.

        Returns:
            list: A list of all stats, combining session and all-time data.
        """
        all_time_stats = self._load_from_file()
        return self.session_stats + all_time_stats

    def get_summary(self):
        """
        Provide a summary of combined stats.

        Returns:
            dict: Summary containing total games, average guesses, and average relevance score.
        """
        combined_stats = self.get_combined_stats()
        if not combined_stats:
            return {
                "total_games": 0,
                "avg_guesses": None,
                "avg_relevance_score": None,
            }

        total_games = len(combined_stats)
        avg_guesses = sum(game["num_guesses"] for game in combined_stats) / total_games
        avg_relevance_score = sum(game["avg_relevance_score"] for game in combined_stats) / total_games

        return {
            "total_games": total_games,
            "avg_guesses": avg_guesses,
            "avg_relevance_score": avg_relevance_score,
        }

    def _load_from_file(self):
        """
        Load all-time stats from the JSON file.

        Returns:
            list: A list of game stats dictionaries.
        """
        try:
            with open(self.stats_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_to_file(self, new_stats):
        """
        Save new stats to the JSON file.

        Args:
            new_stats (dict): A single game's stats to append.
        """
        all_time_stats = self._load_from_file()
        all_time_stats.append(new_stats)
        with open(self.stats_file, "w") as f:
            json.dump(all_time_stats, f)
            
