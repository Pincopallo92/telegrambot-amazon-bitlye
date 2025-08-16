import os
import logging
from amazon_paapi import AmazonApi, AmazonApiException

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

# Keywords di esempio
KEYWORDS = ["laptop", "smartphone", "tablet"]

# Inizializza AmazonApi
amazon = AmazonApi(
    key=AMAZON_ACCESS_KEY,
    secret=AMAZON_SECRET_KEY,
    tag=AMAZON_PARTNER_TAG,
    country=AMAZON_COUNTRY
)

def search_amazon():
    for keyword in KEYWORDS:
        for category in CATEGORIES:
            logging.info(f"Cercando '{keyword}' nella categoria '{category}'")
            for page in range(1, MAX_PAGE_SEARCH + 1):
                try:
                    result = amazon.search_items(
                        keywords=keyword,
                        search_index=category,
                        item_page=page
                    )
                    if hasattr(result, "items"):
                        for item in result.items:
                            title = getattr(item.item_info.title, "display_value", "N/A")
                            url = getattr(item.detail_page_url, "value", "N/A")
                            logging.info(f"{title} - {item.asin} - {url}")
                    else:
                        logging.warning(f"Nessun risultato trovato per '{keyword}' nella categoria '{category}', pagina {page}")
                except AmazonApiException as e:
                    logging.error(f"Errore AmazonAPI: {e}")
                except Exception as e:
                    logging.error(f"Errore generico: {e}")

if __name__ == "__main__":
    search_amazon()
