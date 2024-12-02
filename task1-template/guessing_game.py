from openai import OpenAI
import yaml

class GuessingGame:
    def __init__(self, api_key, instructions="instructions.yaml"):
        """Initialize the GuessingGame class.

        Args:
            api_key (_type_): OpenAI API key.
            instructions (str, optional): Path to the YAML file containing prompts. Defaults to "instructions.yaml".
        """
        self.client = OpenAI(api_key=api_key)
        
        with open(instructions, "r") as file:
            self.prompts = yaml.safe_load(file)
        
        self.used_animals = set()  
        self.conversation_history = []
        self.target_animal = None
        self.game_over = False
        self.start_game()        
        
        
    def reset_game(self):
        self.conversation_history = []
        self.target_animal = None
        self.game_over = False
        self.start_game()
        
        
    def start_game(self, max_retries=3):
        """Start a new guessing game by selecting a target animal

        Args:
            max_retries (int, optional): Maximum attempts to get a valid animal. Defaults to 3.
        """
        start_game_prompt = self.prompts["start_game_prompt"]
        
        # Dynamically generate the exclude clause
        excluded_animals = ", ".join(self.used_animals)
        exclude_clause = ""
        if self.used_animals:
            exclude_clause = self.prompts["exclude_clause"].format(excluded_animals=excluded_animals)
            # Combine the start_game_prompt and exclude clause
            start_game_prompt += "\n" + exclude_clause
        
        # Retry loop to handle invalid responses or duplicates
        for attempt in range(max_retries):
            response = self.client.chat.completions.create(
                messages=[{"role": "system", "content": start_game_prompt}],
                model="gpt-4o-mini"
            )
            raw_output = response.choices[0].message.content.strip()
            
            # Process GPT's response to extract animal name
            if raw_output.startswith("Animal:"):
                selected_animal = raw_output.split("Animal:")[1].strip()
                
                # Check for duplicates
                if selected_animal not in self.used_animals:
                    self.used_animals.add(selected_animal)
                    self.target_animal = selected_animal
                    
                    # Add the target animal to the conversation history
                    self.conversation_history.append(
                        {"role": "system", "content": self.prompts["system_prompt"].format(target_animal=self.target_animal)}
                    )
                    print(f"Target Animal (for debugging): {self.target_animal}")
                    self.game_over = False
                    return
                else:
                    print(f"Duplicate animal received: {selected_animal}")
                    
            # Log invalid format
            print(f"Invalid format received: {raw_output}")
        
        # Raise an error if no valid animal is found after retries
        raise ValueError("Failed to retrieve a valid animal after multiple attempts")
    
    
    def process_question(self, user_input):
        """Process the user's question by answering and evaluating it.

        Args:
            user_input (str): The user's question.
        
        Returns:
            dict: Contains the assistant's response, relevance score, and comment.
        """
        if self.game_over:
            return {"error": "The game is already over. Please reset to start a new game."}
        
        # Step 1: Evaluate the relevance of the question
        relevance_evaluation = self.evaluate_question(user_input)
        
        # Step 2: Generate GPT's answer to the user's question
        assistant_reply = self.answer_question(user_input)
        
        # Return result
        return {
            "response": assistant_reply,  # GPT's answer to the question
            "relevance_score": relevance_evaluation["relevance_score"]  # Includes score and comment
        }
    
    
    def answer_question(self, user_input):
        """Generate GPT's response to the user's question.

        Args:
            user_input (str): The user's question.

        Returns:
            str: GPT's answer to the question
        """
        def parse_reply(assistant_reply):
            try:
                answer, game_over = assistant_reply.split("\n")
                if game_over == "True":
                    return answer, True, True
                elif game_over =="False":
                    return answer, False, True
                else:
                    print("game over state uncertain, defaulting to False")
                    return answer, False, False
            except:
                return "I could not adequately respond to that, you may have strayed from the task too much.", False, False

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.prompts["system_prompt"].format(target_animal=self.target_animal)},
                {"role": "user", "content": user_input}
                ],
            model="gpt-4o-mini"
        )
        
        # Parse assistant response
        assistant_reply = response.choices[0].message.content.strip()
        answer, game_over, add_to_hist = parse_reply(assistant_reply)
        
        # Update states
        if add_to_hist:
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": answer})
            self.game_over = game_over
        
        return answer
    
    def get_known_facts(self):
        # Generate known facts from the conversation history
        known_facts = "\n".join(
            [f"{message["content"]}" for message in self.conversation_history if message["role"] == "assistant"]
        )

        return known_facts if known_facts else "Nothing is known about the animal yet."
    
    
    def evaluate_question(self, user_input):
        """Evaluate the relevance of the user's question based on known facts about the target animal.

        Args:
            user_input (str): The user's question.

        Returns:
            dict: Contains the relevance score and comment.
        """
        # Generate known facts from the conversation history
        known_facts = self.get_known_facts()
                
        # Populate the relevance scoring prompt
        relevance_prompt = self.prompts["relevance_prompt"].format(
            known_facts=known_facts,
            user_input=user_input
        )
        
        # Ask GPT to evaluate the question's relevance
        relevance_response = self.client.chat.completions.create(
            messages=[
                {"role": "user", "content": relevance_prompt}
            ], 
            model="gpt-4o-mini"
        )

        relevance_output = relevance_response.choices[0].message.content.strip()
        
        return {"relevance_score": relevance_output}



    
if __name__ == "__main__":
    api_key = load_api_key()
    game = GuessingGame(api_key)
    #game.start_game()
    response = game.process_question("is it a parrot?")
    print(response)
    response = game.process_question("does it live in water?")
    print(response)
    response = game.process_question("is it a mammal?")
    print(response)
    response = game.process_question("is it an elephant?")
    print(response)
    response = game.process_question("can it fly")
    print(response)
    game.reset_game()
    response = game.process_question("can it fly")
    print(response)
    
    

    
    #game.reset_game()