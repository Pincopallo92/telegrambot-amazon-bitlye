import os
import logging
from amazon_paapi import AmazonApi, Item, SearchResult

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Variabili d'ambiente
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
MAX_PAGE_SEARCH = int(os.environ.get("MAX_PAGE_SEARCH", 3))

# Categorie da cercare
CATEGORIES = ["Electronics", "CellPhones", "Computers"]

# Keyword di esempio
KEYWORDS = ["laptop", "smartphone", "tablet"]

# Inizializza Amazon API
try:
    amazon = AmazonApi(
        key=AMAZON_ACCESS_KEY,
        secret=AMAZON_SECRET_KEY,
        tag=AMAZON_PARTNER_TAG,
        country="IT"
    )
except Exception as e:
    logging.error(f"Errore inizializzazione AmazonApi: {e}")
    raise e

def search_items(keyword, category, max_pages=MAX_PAGE_SEARCH):
    results = []
    for page in range(1, max_pages + 1):
        try:
            logging.info(f"Cercando '{keyword}' nella categoria '{category}', pagina {page}")
            search_result: SearchResult = amazon.search_items(
                keywords=keyword,
                search_index=category,
                item_page=page
            )
            if search_result.items:
                results.extend(search_result.items)
        except Exception as e:
            logging.error(f"Errore AmazonAPI: {e}")
    return results

def main():
    for keyword in KEYWORDS:
        for category in CATEGORIES:
            items = search_items(keyword, category)
            for item in items:
                # Logging sicuro degli attributi esistenti
                title = getattr(item, "title", "N/A")
                asin = getattr(item, "asin", "N/A")
                url = getattr(item, "detail_page_url", "N/A")
                logging.info(f"{title} - {asin} - {url}")

if __name__ == "__main__":
    main()
