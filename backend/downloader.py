import urllib.parse as p

import requests
import io
from PIL import Image
import os


def extract_deck_recipe(url: str) -> str:
    url = p.unquote(url)
    share_param = "u" if "facebook" in url else "url"
    query = p.urlparse(url)
    params = p.parse_qs(query.query)
    if share_param in params.keys():
        params = extract_deck_recipe(params[share_param][0])
        return params
    else:
        return params["deck"][0]


def is_alt_art(card: dict) -> bool:
    ## card img url includes text after the card number in the filename if alt art
    try:
        return card["image_url"].split(card["card_number"])[1] != ".png"
    except Exception:
        ## if this fails, it's also an alt art because it's non-standard format
        return True


def fetch_deck(url_code: str) -> dict:
    url = f"https://api.bandai-tcg-plus.com/api/user/deck/recipe?url_code={url_code}&game_title_id=4"
    deck_request = requests.get(url)
    if deck_request.ok:
        return deck_request.json()["success"]


def save_card(session_id: str, card: dict):
    ## make the session dir if need be
    os.makedirs(session_id, exist_ok=True)
    card_number = card["card_number"]
    card_image_url = card["image_url"]
    card_set = card["card_number"].split("-")[0]
    os.makedirs(f"data/{session_id}/{card_set}", exist_ok=True)
    image_request = requests.get(card_image_url)
    if image_request.ok:
        image = Image.open(io.BytesIO(image_request.content))
        image = image.convert("RGB")
        image.save(f"data/{session_id}/{card_set}/{card_number}.jpg")
        image.thumbnail((120, 167), Image.Resampling.LANCZOS)
        image.save(f"data/{session_id}/{card_set}/{card_number}_small.jpg")


def parse_deck(url_string: str, session_id: str) -> list:
    deck_recipe = extract_deck_recipe(url_string)
    deck = fetch_deck(deck_recipe)
    alt_arts = []
    cards = deck["main_deck"] + deck["extra_deck"] + deck["side_deck"]
    for card in cards:
        if is_alt_art(card):
            save_card(session_id, card)
            alt_arts.append(card["card_number"])
    return alt_arts
