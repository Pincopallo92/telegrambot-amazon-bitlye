import os
import logging
import requests
from amazon_paapi import AmazonApi

# --- Configurazione Logging ---
logging.basicConfig(level=logging.INFO)

# --- Amazon PA-API credentials (usa variabili d'ambiente) ---
AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_ASSOCIATE_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG")
AMAZON_COUNTRY = os.environ.get("AMAZON_COUNTRY", "IT")

# --- Telegram Bot Credentials ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL")

def get_electronics_discounts():
    amazon = AmazonApi(
        AMAZON_ACCESS_KEY,
        AMAZON_SECRET_KEY,
        AMAZON_ASSOCIATE_TAG,
        AMAZON_COUNTRY
    )

    keywords = ["electronics", "smartphone", "tablet", "laptop", "computer"]
    items = []
    for kw in keywords:
        try:
            results = amazon.search_items(
                keywords=kw,
                search_index="Electronics",
                item_count=3,
                resources=[
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis.Price",
                    "Images.Primary.Small",
                    "DetailPageURL",
                ]
            )
            if hasattr(results, "items"):
                items.extend(results.items)
        except Exception as e:
            logging.error(f"Errore ricerca {kw}: {e}")

    discounts = []
    for item in items:
        try:
            title = getattr(item.item_info.title, "display_value", "No Title")
            url = getattr(item, "detail_page_url", "#")

            price = None
            basis_price = None
            discount = ""

            if item.offers and item.offers.listings:
                price_info = item.offers.listings[0].price
                if price_info:
                    price = price_info.amount
                    if price_info.savings and price_info.savings.percentage:
                        discount = f"{price_info.savings.percentage}% off"
                if price_info.saving_basis:
                    basis_price = price_info.saving_basis.amount

            discounts.append({
                "title": title,
                "price": f"{price} €" if price else "N/A",
                "discount": discount,
                "url": url
            })
        except Exception as e:
            logging.error(f"Errore processando item: {e}")

    return discounts

def format_discount_message(discounts):
    if not discounts:
        return "❌ Nessun nuovo sconto trovato."
    message = "🔥 Offerte Amazon in Elettronica:\n"
    for item in discounts:
        line = f"\n• [{item['title']}]({item['url']}) - {item['price']}"
        if item["discount"]:
            line += f" ({item['discount']})"
        message += line
    return message

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()

def main():
    discounts = get_electronics_discounts()
    message = format_discount_message(discounts)
    send_telegram_message(message)
    logging.info("✅ Messaggio inviato al canale Telegram.")

if __name__ == "__main__":
    main()
