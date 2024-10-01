import sys
# Import from other folder -> Ugly
from src.database.database import create_connection
from src.scrapper.scrapper import scrap_poke_data


class Langs(str):
    FR = "fr"
    EN = "en"
    JP = "jp"
    
def main():
    connection = create_connection()
    scrap_poke_data(connection, Langs.FR)
    
    
if __name__ == "__main__":
    sys.exit(main())
