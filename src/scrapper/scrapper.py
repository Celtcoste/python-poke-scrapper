import requests
import time
from enum import Enum

from ..database.bloc import Bloc, BlocTranslation, insert_bloc_translation, insert_bloc
from ..database.set import Set, SetTranslation, insert_set_translation, insert_set
from ..database.illustrator import Illustrator, insert_illustrator
from ..database.card import Card, PokemonCard, insert_card, insert_card_translation, insert_energy_card, insert_trainer_card, insert_pokemon_card, insert_pokemon_card_element, insert_card_variant, get_card_id, check_energy_card, check_trainer_card, check_pokemon_card
from ..database.category import get_category_id_by_name
from ..database.rarity import get_rarity_id_by_name
from ..database.pokemon import insert_pokemon_if_not_exist

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}")
        return None
    
    
language_ids = {
    "fr": 1,
    "en": 2,
    "jp": 3
}
    
tcg_ids = {
    "fr": "poke-fr",
    "en": "poke-en",
    "jp": "poke-jp"
}

api_langs = {
    "fr": "fr",
    "en": "en",
    "jp": "ja"
}

category_enum = {
    "category-energy",
    "category-pokemon",
    "category-trainer"
}

class Category(Enum):
    ENERGY = "category-energy"
    POKEMON = "category-pokemon"
    TRAINER = "category-trainer"
    
category_id_table_name= {
    Category.ENERGY: "energy_card",
    Category.POKEMON: "pokemon_card",
    Category.TRAINER: "trainer_card"
}


def scrap_poke_data(connection, lang: str):
    base_url = f"https://api.tcgdex.net/v2/{api_langs[lang]}"
    blocs_url = f"{base_url}/series"
    sets_url = f"{base_url}/sets"
    cards_url = f"{base_url}/cards"
    
    # Get bloc list
    blocs_data = fetch_data(blocs_url)
    if blocs_data:
        for bloc_position, bloc_data in enumerate(blocs_data, 1):
            # Create the bloc
            bloc_id = insert_bloc(connection, Bloc(f"{tcg_ids[lang]}/{bloc_data["id"]}", 1, bloc_position, tcg_ids[lang]))
            # Add the translation bloc
            insert_bloc_translation(connection, BlocTranslation(f"{bloc_id}/translation", bloc_id, bloc_data["name"], "", language_ids[lang]))
            # Fetch the sets
            sets_data = fetch_data(f"{blocs_url}/{bloc_data["id"]}")
            if sets_data:
                for set_position, set_data in enumerate(sets_data["sets"], 1):
                    # Insert the sets
                    set_id = insert_set(connection, Set(f"{bloc_id}/{set_data["id"]}", set_data["cardCount"]["total"], set_position, bloc_id))
                    # Add translation set
                    insert_set_translation(connection, SetTranslation(f"{set_id}/translation", set_id, set_data["name"], "", language_ids[lang]))
            
                    # Fetch the set cards
                    sets_data = fetch_data(f"{sets_url}/{set_data["id"]}")
                    for card_position, card_global_data in enumerate(sets_data["cards"]): 
                        exist = get_card_id(connection, f"{set_id}/{card_global_data["localId"]}")
                        if exist != 0:
                            if check_pokemon_card(connection, exist) != 0 or check_energy_card(connection, exist) != 0 or check_trainer_card(connection, exist) != 0:
                                print("Already scrapped Card: ", card_global_data["id"], " - ", card_global_data["name"])
                                continue
                        # Fetch the card data
                        card_data = fetch_data(f"{cards_url}/{card_global_data["id"]}")
                        print(card_data)
                        
                        # Add or get the illustrator id
                        if card_data.get("illustrator"):
                            id_illustrator = insert_illustrator(connection, Illustrator(card_data["illustrator"]))
                        else:
                            id_illustrator = insert_illustrator(connection, Illustrator("Unknown"))
                        # Get the category id
                        id_category = get_category_id_by_name(connection, card_data["category"])
                        # Get the rarity id
                        id_rarity = get_rarity_id_by_name(connection, card_data["rarity"])
                        # Insert the card
                        card_id = insert_card(connection, Card(f"{set_id}/{card_data["localId"]}", card_data["localId"], id_category, id_rarity, set_id, id_illustrator))
                        # Add card translation
                        if card_data.get("description"):
                            description = card_data["description"]
                        elif card_data.get("effect"):
                            description = card_data["effect"]
                        else:
                            description = None
                        insert_card_translation(connection, f"{card_id}/translation", card_id, language_ids[lang], card_data["name"], description)
                        
                        # Insert the card type
                        if id_category == Category.ENERGY.value:
                            insert_energy_card(connection, f"{card_id}/energy", card_id, card_data["name"], language_ids[lang])
                        elif id_category == Category.TRAINER.value:
                            insert_trainer_card(connection, f"{card_id}/trainer", card_id)
                        elif id_category == Category.POKEMON.value:
                            if card_data.get("dexId"):
                                # Insert pokemon if not exists
                                pokemon_id = insert_pokemon_if_not_exist(connection, card_data["dexId"][0], f"{lang}/pokemon/{card_data["dexId"][0]}", card_data["name"], language_ids[lang])
                            else:
                                dexId = input("Insert dexID for pokemon (" + card_data["name"] + " and " + card_data["id"]+ "): ")
                                pokemon_id = insert_pokemon_if_not_exist(connection, dexId, f"{lang}/pokemon/{dexId}", card_data["name"], language_ids[lang])
                            # Insert the pokemon card
                            if card_data.get("level"):
                                level = card_data["level"]
                            else:
                                level = 0
                            pokemon_card_id = insert_pokemon_card(connection, PokemonCard( f"{card_id}/pokemon", card_id, pokemon_id, card_data["hp"], level))
                            
                            # Insert the pokemon card elements
                            for type in card_data["types"]:
                                insert_pokemon_card_element(connection, pokemon_card_id, type, language_ids[lang])
                        else:
                            print("Invalid category:", id_category)
                        
                        # Add card variants
                        if card_data["variants"]["firstEdition"] == True:
                            insert_card_variant(connection, card_id, "firstEdition")
                        if card_data["variants"]["holo"] == True:
                            insert_card_variant(connection, card_id, "holo")
                        if card_data["variants"]["normal"] == True:
                            insert_card_variant(connection, card_id, "normal")
                        if card_data["variants"]["reverse"] == True:
                            insert_card_variant(connection, card_id, "reverse")
                        if card_data["variants"]["wPromo"] == True:
                            insert_card_variant(connection, card_id, "wPromo")

                        print("Scrapped card: ", card_data["id"], " - ", card_data["name"])
                        # Sleep to avoid overwhelming the API
                        time.sleep(1)

            print("Scrapped Bloc: ", bloc_data["name"])