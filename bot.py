from typing import Dict, List
import telegram
from amazon_paapi import AmazonApi
from create_messages import create_item_html
import time
from datetime import datetime
import random
import logging
from consts import *  # Assicurati che qui ci siano TOKEN, CHANNEL_NAME, CATEGORIES, ecc.
import os

AMAZON_ACCESS_KEY = os.environ.get("AMAZON_ACCESS_KEY")
AMAZON_SECRET_KEY = os.environ.get("AMAZON_SECRET_KEY")
AMAZON_PARTNER_TAG = os.environ.get("AMAZON_PARTNER_TAG")
AMAZON_HOST = os.environ.get("AMAZON_HOST")
AMAZON_REGION = os.environ.get("AMAZON_REGION")
CHANNEL_NAME = os.environ.get("CHANNEL_NAME")
TOKEN = os.environ.get("TOKEN")
default_api = AmazonApi(
    key=AMAZON_ACCESS_KEY,
    secret=AMAZON_SECRET_KEY,
    tag=AMAZON_PARTNER_TAG,
    country=AMAZON_REGION
)

logging.basicConfig(level=logging.INFO)

# ******  Author: Paolo Francioso ********

def is_active() -> bool:
    now = datetime.now().time()
    return MIN_HOUR < now.hour < MAX_HOUR

def send_consecutive_messages(list_of_struct: List[str], number_of_messages=int) -> None:
    for i in range(number_of_messages):
        pointer_1 = 0 + i * 2
        pointer_2 = 1 + i * 2
        bot.send_message(
            chat_id=CHANNEL_NAME,
            text=list_of_struct[pointer_1],
            reply_markup=list_of_struct[pointer_2],
            parse_mode=telegram.ParseMode.HTML,
        )
    return_counter = pointer_2 + 1    
    return list_of_struct[return_counter:]

# Funzione per cercare prodotti su Amazon usando AmazonApi
def search_items(keywords, search_index="All", item_page=1):
    api = AmazonApi(
        access_key=AMAZON_ACCESS_KEY,
        secret_key=AMAZON_SECRET_KEY,
        partner_tag=AMAZON_PARTNER_TAG,
        host=AMAZON_HOST,
        region=AMAZON_REGION
    )
    try:
        response = api.search_items(
            keywords=keywords,
            search_index=search_index,
            item_page=item_page
        )
        return response.items if response.items else []
    except Exception as e:
        logging.info(f"Errore nella ricerca Amazon: {e}")
        return []

def run_bot(bot: telegram.Bot, categories: Dict[str, List[str]]) -> None:
    min_result = NUMBER_OF_MESSAGES*2 - 1
    res_except = NUMBER_OF_MESSAGES*2

    while True:
        try:
            items_full = []

            # randomizza categorie e keyword
            randomizer = len(categories) - 1
            random_array = random.randint(0, randomizer)
            
            counter = 0
            try:
                for category in categories:
                    if counter == random_array:
                        random.shuffle(categories[category])
                        for keyword in categories[category]:
                            for page in range(1, MAX_PAGE_SEARCH):
                                items = search_items(keyword, category, item_page=page)
                                time.sleep(1)
                                if items:
                                    items_full.extend(items)
                            raise StopIteration
                    counter += 1
            except StopIteration:
                pass

            logging.info(f'{5 * "*"} Requests Completed {5 * "*"}')
            random.shuffle(items_full)
            res = create_item_html(items_full, False)

            while len(res) > min_result:
                if is_active():
                    try:
                        logging.info(f'{5 * "*"} Sending posts to channel {5 * "*"}')
                        res = send_consecutive_messages(res, NUMBER_OF_MESSAGES)
                    except Exception as e:
                        logging.info(e)
                        res = res[res_except:]
                        continue
                    time.sleep(60 * PAUSE_MINUTES)
                else:
                    logging.info(f'{5 * "*"} Inactive Bot, between {MIN_HOUR}AM and {MAX_HOUR}PM {5 * "*"}')
                    time.sleep(60 * 5)

        except Exception as e:
            logging.info(e)
            break

if __name__ == "__main__":
    bot = telegram.Bot(token=TOKEN)
    run_bot(bot=bot, categories=CATEGORIES)
