import requests
from tqdm import tqdm
import os
from trello_api import get_workspaces
from trello_api import get_workspaces
from trello_api import get_boards
from trello_api import get_lists
from trello_api import get_cards
from trello_api import get_card_attachments
from trello_api import get_card_comments
from config import PLANKA_URL, USERNAME, PASSWORD, APIKEY, APITOKEN

# Function: authorisation and receipt of Bearer token for Planka
def get_token():
    url = f"{PLANKA_URL}/access-tokens"
    payload = {"emailOrUsername": USERNAME, "password": PASSWORD}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["item"]

# Function: logging messages to a log file and output to the console
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "log.txt")
def log_message(message):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(message + "\n")
    print(message)

# Function: counts the number of items in Trello to check the transfer totals
def count_trello_items():
    items = {"workspaces": 0, "boards": 0, "lists": 0, "cards": 0, "attachments": 0, "comments": 0}
    
    workspaces = get_workspaces()
    items["workspaces"] = len(workspaces)

    for ws in tqdm(workspaces, desc="Board count"):  
        boards = get_boards(ws["id"])
        items["boards"] += len(boards)

        for board in tqdm(boards, desc="Counting lists", leave=False):  
            lists = get_lists(board["id"])
            items["lists"] += len(lists)

            for lst in tqdm(lists, desc="Card counting", leave=False):  
                cards = get_cards(lst["id"])
                items["cards"] += len(cards)

                for card in tqdm(cards, desc="Counting attachments and comments", leave=False):  
                    items["attachments"] += len(get_card_attachments(card["id"], APIKEY, APITOKEN))
                    items["comments"] += len(get_card_comments(card["id"]))

    return items