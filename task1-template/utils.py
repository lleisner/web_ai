from dotenv import load_dotenv
import os

def load_api_key(env_path="~/.env", key_name="OPENAI_API_KEY"):
    """
    Load an API key from a specified .env file.
    
    Args:
        env_path (str): Path to the .env file (default is '~/.env').
        key_name (str): The environment variable name (default is 'OPENAI_API_KEY').
    
    Returns:
        str: The API key, or None if not found.
    """
    resolved_path = os.path.expanduser(env_path)
    load_dotenv(dotenv_path=resolved_path)
    return os.getenv(key_name)
