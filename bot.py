import os
import time
import random
from amazon_paapi import AmazonApi
import requests

# --- Amazon PA-API credentials ---
AMAZON_ACCESS_KEY = "YOUR_ACCESS_KEY"
AMAZON_SECRET_KEY = "YOUR_SECRET_KEY"
AMAZON_ASSOCIATE_TAG = "YOUR_ASSOCIATE_TAG"
AMAZON_COUNTRY = "IT"  # e.g., 'US', 'IT', 'DE', etc.

# --- Telegram Bot Credentials ---
TELEGRAM_BOT_TOKEN = "7639507455:AAFxqE-xEc7MxBY0MzhH2PGQ01_pvs0QPl4"
TELEGRAM_CHANNEL = "@lowpriceamazonitaly"  # Or numeric channel ID

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
                item_count=3,  # Adjust how many items per keyword
                resources=[
                    "ItemInfo.Title",
                    "Offers.Listings.Price",
                    "Offers.Listings.SavingBasis.Price",
                    "Offers.Summaries.HighestPrice",
                    "Offers.Summaries.LowestPrice",
                    "Images.Primary.Small",
                    "DetailPageURL",
                ]
            )
            items.extend(results.items)
        except Exception as e:
            print(f"Error fetching items for {kw}: {e}")

    discounts = []
    for item in items:
        try:
            title = item.title or "No Title"
            url = item.detail_page_url or "#"
            price = item.prices.get('price') if item.prices else "N/A"
            basis_price = item.prices.get('saving_basis_price') if item.prices else None
            if price != "N/A" and basis_price and float(basis_price) > float(price):
                discount = f"{round((float(basis_price) - float(price))/float(basis_price)*100, 1)}% off"
            else:
                discount = ""
            discounts.append({
                "title": title,
                "price": price,
                "discount": discount,
                "url": url
            })
        except Exception as e:
            print(f"Error processing item: {e}")

    # Only return discounts with a real discount
    discounts = [d for d in discounts if d["discount"]]
    return discounts

def format_discount_message(discounts):
    # Only called if there are objects
    message = "🔥 Latest Electronics Discounts on Amazon:\n"
    for item in discounts:
        title = item["title"]
        price = item["price"]
        discount = item["discount"]
        url = item["url"]
        line = f"\n• [{title}]({url}) - {price} ({discount})"
        message += line
    return message

def send_telegram_message(text):
    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )
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
    while True:
        try:
            discounts = get_electronics_discounts()
            if discounts:
                message = format_discount_message(discounts)
                send_telegram_message(message)
                print("Message sent to Telegram channel.")
            else:
                print("No discounts found. No message sent.")
        except Exception as e:
            print(f"Error: {e}")

        # Sleep for a random interval between 50 and 70 minutes
        sleep_minutes = random.randint(50, 70)
        print(f"Sleeping for {sleep_minutes} minutes...")
        time.sleep(sleep_minutes * 60)

if __name__ == "__main__":
    main()
