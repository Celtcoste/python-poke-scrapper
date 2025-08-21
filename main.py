import sys
import os
from dotenv import load_dotenv
# Import from other folder -> Ugly
from src.database.database import create_connection
from src.scrapper.scrapper import scrap_poke_data
from src.config import setup_debug_mode


class Langs(str):
    FR = "fr"
    EN = "en"
    JP = "jp"
    
def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Setup debug mode from environment variable
    setup_debug_mode()
    
    connection = create_connection()
    scrap_poke_data(connection, Langs.FR)
    
    
if __name__ == "__main__":
    sys.exit(main())
