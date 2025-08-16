import os
import logging
from amazon_paapi import AmazonApi, SearchResult
from flask import Flask
import time

# Configurazione logging
logging.basicConfig(level=logging.INFO)

# Variabili da Render
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")
MAX_PAGE_SEARCH = int(os.environ.get("MAX_PAGE_SEARCH", 3))

# Categorie di esempio
CATEGORIES = ["Electronics", "Computers", "Mobile"]

# Inizializza AmazonApi
amazon = AmazonApi(
    key=AMAZON_ACCESS_KEY,
    secret=AMAZON_SECRET_KEY,
    tag=AMAZON_PARTNER_TAG,
    country=AMAZON_COUNTRY
)

# Flask per Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot attivo"

# Funzione principale di ricerca
def search_amazon():
    keywords = ["laptop", "smartphone", "tablet"]  # puoi aggiungere altre parole chiave
    for keyword in keywords:
        for category in CATEGORIES:
            logging.info(f"Cercando '{keyword}' nella categoria '{category}'")
            for page in range(1, MAX_PAGE_SEARCH + 1):
                try:
                    # AmazonApi restituisce SearchResult, usare .items
                    result: SearchResult = amazon.search_items(
                        keywords=keyword,
                        search_index=category,
                        item_page=page
                    )
                    for item in result.items:
                        # Logging dei dettagli
                        logging.info(f"{item.item_info.title.display_value} - {item.asin} - {item.detail_page_url}")
                    time.sleep(1)  # evita throttling
                except Exception as e:
                    logging.error(f"Errore AmazonAPI: {e}")
                    time.sleep(5)  # attesa prima di riprovare

if __name__ == "__main__":
    # Avvia il bot in background e Flask
    from threading import Thread
    t = Thread(target=search_amazon)
    t.start()
    app.run(host="0.0.0.0", port=10000)
