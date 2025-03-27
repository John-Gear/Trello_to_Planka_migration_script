import requests
from config import TRELLO_URL, APIKEY, APITOKEN

# Function: get a list of Trello workspaces
def get_workspaces():
    url = f"{TRELLO_URL}members/me/organizations"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: get list of boards from Trello
def get_boards(workspace_id):
    url = f"{TRELLO_URL}organizations/{workspace_id}/boards"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieve list from Trello
def get_lists(board_id):
    url = f"{TRELLO_URL}boards/{board_id}/lists"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieve cards from Trello
def get_cards(list_id):
    url = f"{TRELLO_URL}lists/{list_id}/cards"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: get attachments from cards from Trello
def get_card_attachments(card_id, APIKEY, APITOKEN):
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    params = {
        "key": APIKEY,
        "token": APITOKEN
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: gets the ID of an attachment that is a card cover in Trello to transfer it as a cover to a card in Planka
def get_card_cover_attachment_id(card_id):
    url = f"{TRELLO_URL}cards/{card_id}"
    params = {"key": APIKEY, "token": APITOKEN, "fields": "idAttachmentCover"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("idAttachmentCover")

# Function: retrieves all checklists (task list) from a Trello card
def get_card_checklists(card_id):
    url = f"{TRELLO_URL}cards/{card_id}/checklists"
    params = {"key": APIKEY, "token": APITOKEN}
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

# Function: retrieves card comments from Trello
def get_card_comments(card_id):
    url = f"{TRELLO_URL}cards/{card_id}/actions"
    params = {"key": APIKEY, "token": APITOKEN, "filter": "commentCard", "limit": 50}

    all_comments = []
    while True:
        response = requests.get(url, params=params)
        response.raise_for_status()
        comments = response.json()

        if not comments:
            break

        all_comments.extend(comments)
        params["before"] = comments[-1]["id"]

    return all_comments