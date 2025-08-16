import os
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

    # Example keywords and categories: "electronics", "smartphone", "tablet", "laptop", etc.
    # You can adjust this list or refine your queries.
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
    
    # Filter and format discounts
    discounts = []
    for item in items:
        try:
            title = item.title or "No Title"
            url = item.detail_page_url or "#"
            price = item.prices.get('price') if item.prices else "N/A"
            # PA-API does not always give explicit discount info, so you may need to calculate it
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

    return discounts

def format_discount_message(discounts):
    if not discounts:
        return "No new electronics discounts found."
    message = "🔥 Latest Electronics Discounts on Amazon:\n"
    for item in discounts:
        title = item["title"]
        price = item["price"]
        discount = item["discount"]
        url = item["url"]
        line = f"\n• [{title}]({url}) - {price}"
        if discount:
            line += f" ({discount})"
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
    try:
        discounts = get_electronics_discounts()
        message = format_discount_message(discounts)
        send_telegram_message(message)
        print("Message sent to Telegram channel.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
