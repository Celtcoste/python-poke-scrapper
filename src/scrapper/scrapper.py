import requests
import time
from enum import Enum
from ..utils.logger import debug, info, error

from ..database.bloc import Bloc, BlocTranslation, insert_bloc_translation, insert_bloc, get_tcg_language_id_by_slug
from ..database.set import Set, SetTranslation, insert_set_translation, insert_set, get_set_id_by_slug
from ..database.illustrator import Illustrator, insert_illustrator
from ..database.card import Card, PokemonCard, insert_card, insert_card_translation, insert_energy_card, insert_trainer_card, insert_pokemon_card, insert_pokemon_card_element, insert_card_variant, get_card_id, check_energy_card, check_trainer_card, check_pokemon_card
from ..database.category import get_category_id_by_name
from ..database.rarity import get_rarity_id_by_name, insert_card_rarity
from ..database.pokemon import insert_pokemon_if_not_exist, get_pokemon_id_by_name

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        error("Failed to fetch data from %s", url)
        return None
    
    
language_ids = {
    "fr": 1,
    "en": 2,
    "jp": 3
}
    
tcg_language_ids = {
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

# Dynamic category ID mapping - will be populated at runtime
CATEGORY_IDS = {}

def get_category_ids_mapping(connection):
    """Get the actual category IDs from database"""
    global CATEGORY_IDS
    if not CATEGORY_IDS:  # Only load once
        cursor = connection.cursor()
        try:
            cursor.execute("""
                SELECT c.slug, c.id 
                FROM category c 
                ORDER BY c.id
            """)
            categories = cursor.fetchall()
            debug("Found categories in database: %s", categories)
            
            # Map category slugs to IDs
            for slug, cat_id in categories:
                if 'energy' in slug.lower():
                    CATEGORY_IDS['ENERGY'] = cat_id
                elif 'pokemon' in slug.lower():
                    CATEGORY_IDS['POKEMON'] = cat_id
                elif 'trainer' in slug.lower():
                    CATEGORY_IDS['TRAINER'] = cat_id
            
            debug("Category ID mapping: %s", CATEGORY_IDS)
                    
        except Exception as err:
            error("Error loading category IDs: %s", err)
        finally:
            cursor.close()
    
    return CATEGORY_IDS

# Legacy enum for backward compatibility
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
    # Load category IDs from database
    category_ids = get_category_ids_mapping(connection)
    
    base_url = f"https://api.tcgdex.net/v2/{api_langs[lang]}"
    blocs_url = f"{base_url}/series"
    sets_url = f"{base_url}/sets"
    cards_url = f"{base_url}/cards"
    
    # Get bloc list
    blocs_data = fetch_data(blocs_url)
    debug("Blocs data: %s", blocs_data)
    if blocs_data:
        for bloc_position, bloc_data in enumerate(blocs_data, 1):
            # if bloc_data["id"] != "sv":
            #     debug("Skipping bloc: %s", bloc_data["id"])
            #     continue
            info("Scrapping bloc: %s", bloc_data["id"])
            
            # Get the actual tcg_language_id (integer) from database
            tcg_lang_id = get_tcg_language_id_by_slug(connection, tcg_language_ids[lang])
            if tcg_lang_id is None:
                error("TCG Language ID not found for slug: %s", tcg_language_ids[lang])
                continue
                
            # Create bloc slug in the format: poke-fr/sv
            bloc_slug = f"{tcg_language_ids[lang]}/{bloc_data['id']}"
            
            debug("Creating bloc with slug: '%s' and tcg_language_id: %s", bloc_slug, tcg_lang_id)
            # Create the bloc (id, set_number, position, tcg_id)
            bloc_id = insert_bloc(connection, Bloc(bloc_slug, 1, bloc_position, tcg_lang_id))
            
            if bloc_id is None:
                error("Failed to create bloc '%s'. Skipping...", bloc_slug)
                continue
                
            # Add the translation bloc
            translation_slug = f"{bloc_slug}/translation/{api_langs[lang]}"
            insert_bloc_translation(connection, BlocTranslation(translation_slug, bloc_id, bloc_data["name"], "", language_ids[lang]))
            # Fetch the sets
            sets_data = fetch_data(f"{blocs_url}/{bloc_data["id"]}")
            if sets_data:
                for set_position, set_data in enumerate(sets_data["sets"], 1):
                    # Insert the sets
                    # Create set slug in the format: poke-fr/sv/sv1 (using bloc slug + clean set id)
                    set_slug = f"{bloc_slug}/{set_data['id']}"
                    
                    debug("Creating set with slug: '%s' and bloc_id: %s", set_slug, bloc_id)
                    set_id = insert_set(connection, Set(set_slug, set_data["cardCount"]["total"], set_position, bloc_id))
                    
                    if set_id is None:
                        error("Failed to create set '%s'. Skipping...", set_slug)
                        continue
                        
                    # Add translation set
                    set_translation_slug = f"{set_slug}/translation/{api_langs[lang]}"
                    insert_set_translation(connection, SetTranslation(set_translation_slug, set_id, set_data["name"], "", language_ids[lang]))
            
                    # Fetch the set cards
                    sets_data = fetch_data(f"{sets_url}/{set_data["id"]}")
                    for card_position, card_global_data in enumerate(sets_data["cards"]): 
                        # Create card slug in the format: set_slug/card_localId (with cleaned format)
                        card_slug = f"{set_slug}/{card_global_data['localId']}"
                        
                        debug("Processing card with slug: '%s' (position: %s)", card_slug, card_global_data['localId'])
                        exist = get_card_id(connection, card_slug)
                        if exist != 0:
                            if check_pokemon_card(connection, exist) != 0 or check_energy_card(connection, exist) != 0 or check_trainer_card(connection, exist) != 0:
                                debug("Already scrapped Card: %s - %s", card_global_data["id"], card_global_data["name"])
                                continue
                        # Fetch the card data
                        card_data = fetch_data(f"{cards_url}/{card_global_data["id"]}")
                        if card_data == None:
                            continue
                        debug("Card data: %s", card_data)
                        
                        # Add or get the illustrator id
                        if card_data.get("illustrator"):
                            id_illustrator = insert_illustrator(connection, Illustrator(card_data["illustrator"]))
                        else:
                            id_illustrator = insert_illustrator(connection, Illustrator("Unknown"))
                        # Get the category id
                        id_category = get_category_id_by_name(connection, card_data["category"])
                        # Get the rarity id
                        id_rarity = get_rarity_id_by_name(connection, card_data["rarity"])
                        # Insert the card (use cleaned position format)
                        card_id = insert_card(connection, Card(card_slug, card_data["localId"], id_category, id_rarity, set_id, id_illustrator))
                        
                        if card_id is None:
                            error("Failed to create card '%s'. Skipping...", card_slug)
                            error("Card data received from API: %s", card_data)
                            error("Card object details: slug='%s', position='%s', category_id=%s, rarity_id=%s, set_id=%s, illustrator_id=%s", 
                                  card_slug, card_data["localId"], id_category, id_rarity, set_id, id_illustrator)
                            continue
                            
                        # Add card translation
                        if card_data.get("description"):
                            description = card_data["description"]
                        elif card_data.get("effect"):
                            description = card_data["effect"]
                        else:
                            description = None
                        card_translation_slug = f"{card_slug}/translation/{api_langs[lang]}"
                        translation_id = insert_card_translation(connection, card_translation_slug, card_id, language_ids[lang], card_data["name"], description)
                        
                        if translation_id is None:
                            error("Failed to create card translation for card_id=%s", card_id)
                            error("Card translation data: slug='%s', name='%s', description='%s', language_id=%s", 
                                  card_translation_slug, card_data["name"], description, language_ids[lang])
                            error("Original card data: %s", card_data)
                        
                        # Insert the card type
                        debug("Processing card type with category ID: %s", id_category)
                        debug("Available category IDs: %s", CATEGORY_IDS)
                        
                        if id_category == CATEGORY_IDS.get('ENERGY', -1):
                            energy_card_slug = f"{card_slug}/energy"
                            energy_result = insert_energy_card(connection, energy_card_slug, card_id, card_data["name"], language_ids[lang])
                            if energy_result is None:
                                error("Failed to create energy card for card_id=%s", card_id)
                                error("Energy card data: slug='%s', energy_type='%s'", energy_card_slug, card_data["name"])
                                error("Original card data: %s", card_data)
                        elif id_category == CATEGORY_IDS.get('TRAINER', -1):
                            trainer_card_slug = f"{card_slug}/trainer"
                            trainer_result = insert_trainer_card(connection, trainer_card_slug, card_id)
                            if trainer_result is None:
                                error("Failed to create trainer card for card_id=%s", card_id)
                                error("Trainer card data: slug='%s'", trainer_card_slug)
                                error("Original card data: %s", card_data)
                        elif id_category == CATEGORY_IDS.get('POKEMON', -1):
                            if card_data.get("dexId"):
                                # Insert pokemon if not exists
                                # Clean the slug format for pokemon translation
                                pokemon_slug = f"{lang}/pokemon/{card_data['dexId'][0]}"
                                pokemon_id = insert_pokemon_if_not_exist(connection, card_data["dexId"][0], pokemon_slug, card_data["name"], language_ids[lang])
                                if pokemon_id is None:
                                    error("Failed to create pokemon for dex_id=%s", card_data["dexId"][0])
                                    error("Pokemon data: slug='%s', name='%s'", pokemon_slug, card_data["name"])
                                    error("Original card data: %s", card_data)
                            else:
                                dexId = get_pokemon_id_by_name(connection, card_data["name"].split(' ')[0], language_ids[lang])
                                if dexId == 0:
                                    if len(card_data["name"].split(' ')) > 1:
                                        dexId = get_pokemon_id_by_name(connection, card_data["name"].split(' ')[1], language_ids[lang])
                                if dexId == 0:
                                    dexId = get_pokemon_id_by_name(connection, card_data["name"].split('-ex')[0], language_ids[lang])
                                    if dexId == 0:
                                        dexId = input("Insert dexID for pokemon (" + card_data["name"] + " and " + card_data["id"]+ "): ")
                                # Clean the slug format for pokemon translation
                                pokemon_slug = f"pokemon/{dexId}/{lang}"
                                pokemon_id = insert_pokemon_if_not_exist(connection, dexId, pokemon_slug, card_data["name"], language_ids[lang])
                                if pokemon_id is None:
                                    error("Failed to create pokemon for dex_id=%s", dexId)
                                    error("Pokemon data: slug='%s', name='%s'", pokemon_slug, card_data["name"])
                                    error("Original card data: %s", card_data)
                            # Insert the pokemon card
                            if card_data.get("level"):
                                level = card_data["level"]
                            else:
                                level = 0
                            if card_data.get("hp"):
                                hp = card_data["hp"]
                            else:
                                hp = 0
                            pokemon_card_slug = f"{card_slug}/pokemon"
                            pokemon_card_id = insert_pokemon_card(connection, PokemonCard(pokemon_card_slug, card_id, pokemon_id, hp, level))
                            
                            if pokemon_card_id is None:
                                error("Failed to create pokemon card for card_id=%s", card_id)
                                error("Pokemon card data: slug='%s', pokemon_id=%s, hp=%s, level=%s", pokemon_card_slug, pokemon_id, hp, level)
                                error("Original card data: %s", card_data)
                            
                            if  card_data.get("types"):
                                # Insert the pokemon card elements
                                for type in card_data["types"]:
                                    insert_pokemon_card_element(connection, pokemon_card_id, type, language_ids[lang])
                        else:
                            error("Invalid category: %s", id_category)
                        
                        # Add card rarity relationship
                        rarity_result = insert_card_rarity(connection, card_id, card_data["rarity"])
                        if rarity_result is None:
                            error("Failed to create card rarity for card_id=%s with rarity='%s'", card_id, card_data["rarity"])
                        else:
                            debug("Successfully added rarity '%s' (rarity_id=%s) to card_id=%s", card_data["rarity"], rarity_result, card_id)
                        
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

                        info("Scrapped card: %s - %s", card_data["id"], card_data["name"])
                        # Sleep to avoid overwhelming the API
                        time.sleep(0.5)

            info("Scrapped Bloc: %s", bloc_data["name"])