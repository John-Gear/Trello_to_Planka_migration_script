import requests
import unidecode
import datetime
import os
import pytz
from config import PLANKA_URL
from utils import log_message

# Function: creating a project in Planka
def create_project(token, name="test"):
    url = f"{PLANKA_URL}/projects"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"name": name, "description": "Imported from Trello", "isPublic": False}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["item"]

# Function: creating a board in Planka
def create_board(token, project_id, name="test"):
    if not project_id:
        raise ValueError("Error: project_id is empty, board cannot be created!")
    url = f"{PLANKA_URL}/projects/{project_id}/boards"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"name": name, "position": 0, "isPublic": False}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["item"]

# Function: creating a list in Planka
def create_list(token, board_id, name="test"):
    if not board_id:
        raise ValueError("Error: board_id is empty, list could not be created!")
    url = f"{PLANKA_URL}/boards/{board_id}/lists"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"name": name, "position": 0, "boardId": board_id}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["item"]

# Function: creating a card in Planka
def create_card(token, list_id, name, description=None, due_date=None, completed=False):
    if not list_id:
        raise ValueError("Error: list_id is empty, card cannot be created!")

    url = f"{PLANKA_URL}/lists/{list_id}/cards"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    payload = {
        "name": name,
        "position": 0,
        "listId": list_id,
        "isDueDateCompleted": completed
    }

    if due_date:
        payload["dueDate"] = due_date
    if description:
        payload["description"] = description

    log_message(f"Card migration: {name}")

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in [200, 201]:
        log_message(f"Error when creating a card: {response.status_code} - {response.text}")
        response.raise_for_status()

    return response.json()["item"]

# Function: creating a task in a card in Planka (with status saved as completed/uncompleted)
def create_task(token, card_id, name="test task", is_completed=False):
    if not card_id:
        raise ValueError("Error: card_id is empty, task cannot be created!")

    url = f"{PLANKA_URL}/cards/{card_id}/tasks"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "cardId": card_id,
        "name": name,
        "isCompleted": is_completed,
        "position": 0
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["item"]

# Function: creating a comment in a card in Planka (with signature author, date, time of creation in Trello)
def add_comment(token, card_id, text, author_name, author_username, date):
    try:
        formatted_date = datetime.datetime.fromisoformat(date.replace("Z", "")).strftime("%d-%m-%Y %H:%M:%S")
    except ValueError:
        formatted_date = date

    formatted_text = f"""{text}

---
*Imported comment from Trello, originally posted by*  
{author_name} ({author_username})  
{formatted_date}"""

    url = f"{PLANKA_URL}/cards/{card_id}/comment-actions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"text": formatted_text, "cardId": card_id}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["item"]

# Function: creating card attachments in Planka (with signature date and time of creation in Trello)
def add_attachment(token, card_id, file_path, original_date):
    if original_date:
        log_message(f"The original date the file was uploaded to Trello: {original_date}")

    url = f"{PLANKA_URL}/cards/{card_id}/attachments"
    headers = {"Authorization": f"Bearer {token}"}

    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()

    attachment = response.json()["item"]

    return attachment

# Function: converts the file name to Latin if there are non-Latin characters (file name transliteration)
def transliterate_filename(filename):
    base, ext = os.path.splitext(filename)
    transliterated = unidecode.unidecode(base)
    safe_name = transliterated.replace(" ", "_")
    return safe_name + ext

# Function: converts the UTC time of an attachment download from Trello to the user's local time
def convert_to_trello_timezone(utc_time_str, trello_tz="Europe/Moscow"): # set your local timezone
    trello_timezone = pytz.timezone(trello_tz)
    utc_dt = datetime.datetime.fromisoformat(utc_time_str.replace("Z", "")).replace(tzinfo=datetime.timezone.utc)
    local_dt = utc_dt.astimezone(trello_timezone)
    return local_dt.strftime("%d-%m-%Y %H-%M")

# Function: create a label in Planka (if it does not exist)
def create_label(token, board_id, name, color):
    url = f"{PLANKA_URL}/boards/{board_id}/labels"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "boardId": board_id,
        "position": 0,
        "color": color
    }
    
    if name.strip():
        payload["name"] = name

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        return response.json().get("item")

    log_message(f"Label creation error: {response.status_code} - {response.text}")
    return None

# Function: add an existing tag to a card in Planka (tag binding)
def add_label_to_card(token, card_id, label_id):
    url = f"{PLANKA_URL}/cards/{card_id}/labels"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"labelId": label_id}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        return response.json().get("item")
    return None

# Function: update/delete the cover in a card in Planka (if it has not been assigned in a card in Trello)
def update_card_cover(token, card_id, cover_attachment_id):
    url = f"{PLANKA_URL}/cards/{card_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"coverAttachmentId": cover_attachment_id if cover_attachment_id else None}

    response = requests.patch(url, json=payload, headers=headers)
    response.raise_for_status()
    log_message(f"Transferred and installed the card cover")