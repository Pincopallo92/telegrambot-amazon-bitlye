import os
import logging
from amazon_paapi import AmazonApi

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Variabili ambientali
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
MAX_PAGE_SEARCH = int(os.environ.get("MAX_PAGE_SEARCH", 3))

# Categorie da cercare
CATEGORIES = ["Electronics", "Computers", "CellPhones"]

# Inizializza AmazonApi
try:
    amazon = AmazonApi(
        key=AMAZON_ACCESS_KEY,
        secret=AMAZON_SECRET_KEY,
        tag=AMAZON_PARTNER_TAG,
        country=AMAZON_COUNTRY
    )
except Exception as e:
    logging.error(f"Errore inizializzazione AmazonApi: {e}")
    exit(1)

def search_items(keyword, category):
    results = []
    for page in range(1, MAX_PAGE_SEARCH + 1):
        try:
            search_result = amazon.search_items(
                keywords=keyword,
                search_index=category,
                item_page=page
            )
            if hasattr(search_result, "items") and search_result.items:
                results.extend(search_result.items)
        except Exception as e:
            logging.error(f"Errore AmazonAPI: {e}")
            break
    return results


# Esempio di utilizzo
if __name__ == "__main__":
    keyword = "laptop"
    for category in CATEGORIES:
        logging.info(f"Cercando '{keyword}' nella categoria '{category}'")
        items = search_items(keyword, category)
        for item in items:
            logging.info(f"{item.title} - {item.asin} - {item.detail_page_url}")
