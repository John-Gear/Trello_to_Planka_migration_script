import urllib.parse
import requests
import os
import time
from config import APIKEY, APITOKEN
from utils import log_message
from utils import get_token
from utils import count_trello_items
from labels_planka import get_planka_label_color
from planka_api import transliterate_filename
from planka_api import add_attachment
from planka_api import update_card_cover
from planka_api import add_label_to_card
from planka_api import create_label
from planka_api import create_project
from planka_api import create_board
from planka_api import create_card
from planka_api import create_list
from planka_api import create_task
from planka_api import add_comment
from trello_api import get_workspaces
from trello_api import get_boards
from trello_api import get_lists
from trello_api import get_cards
from trello_api import get_card_checklists
from trello_api import get_card_comments
from trello_api import get_card_cover_attachment_id
from trello_api import get_card_attachments
from planka_api import convert_to_trello_timezone

# Function transfers attachments from Trello to Planka, preserving the upload date and cover (optionally with the original creation date added)
ADD_DATE_TO_FILENAME = True  # Flag: True - add date to file name, False - leave original name
def migrate_attachments(token, card_id_planka, card_id_trello):
    attachments = get_card_attachments(card_id_trello, APIKEY, APITOKEN)
    cover_attachment_id = get_card_cover_attachment_id(card_id_trello)

    if not attachments:
        log_message(f"There are no attachments for the card, nothing has been uploaded")
        return

    planka_attachments = {}
    
    for attachment in attachments:
        attachment_id = attachment["id"]

        raw_file_name = attachment.get("name") or urllib.parse.unquote(attachment.get("fileName", "attachment"))
        MAX_FILENAME_LENGTH = 200
        if len(raw_file_name) > MAX_FILENAME_LENGTH:
            raw_file_name = raw_file_name[:MAX_FILENAME_LENGTH] + "..."
        file_name_translit = transliterate_filename(raw_file_name)
        created_at = attachment.get("date", None)

        # Add the date to the file name if the flag is enabled
        if ADD_DATE_TO_FILENAME and created_at:
            try:
                date_str = f"(created_at_{convert_to_trello_timezone(created_at, 'Europe/Moscow')})" # Select the timezone you're in
                base, ext = os.path.splitext(file_name_translit)
                file_name_translit = f"{base}_{date_str}{ext}"
            except ValueError:
                log_message(f"Date processing error {created_at} for file {file_name_translit}, leave original name")

        file_path = f"/tmp/{file_name_translit}"

        if len(file_path) > 255:
            log_message(f"Error: File ‘{raw_file_name}’ has exceeded the path length limit after processing and will be skipped")
            continue

        download_url = f"https://api.trello.com/1/cards/{card_id_trello}/attachments/{attachment_id}/download/{urllib.parse.quote(raw_file_name)}"
        headers = {"Authorization": f'OAuth oauth_consumer_key="{APIKEY}", oauth_token="{APITOKEN}"'}

        try:
            with requests.get(download_url, headers=headers, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            log_message(f"Loading error in Planka {raw_file_name}: {e}")
            continue

        try:
            planka_attachment = add_attachment(token, card_id_planka, file_path, created_at)
            planka_attachments[attachment_id] = planka_attachment["id"]
            log_message(f"The attachment {file_name_translit} has been uploaded to the card")
        except requests.exceptions.RequestException as e:
            log_message(f"Loading error in Planka {file_name_translit}: {e}")
            continue

        os.remove(file_path)

    # Search for a cover by file name if the cover ID is known
    cover_planka_id = planka_attachments.get(cover_attachment_id)
    update_card_cover(token, card_id_planka, cover_planka_id)

# Function to transfer labels from Trello to Planka, preserving order
label_cache = {}  # Global dictionary to cache created labels (to avoid duplicate labels)
def migrate_card_labels(token, board_id, card_id_planka, card_trello):
    global label_cache

    labels = card_trello.get("labels", [])
    if not labels:
        log_message("There are no labels on the card")
        return

    log_message(f"Labels transfer:: {', '.join([l['color'] for l in labels])}")

    for label in reversed(labels):
        trello_color = label.get("color", "gray")
        label_name = label.get("name", "").strip()
        planka_color = get_planka_label_color(trello_color)

        label_key = f"{board_id}_{label_name}_{planka_color}"

        if label_key in label_cache:
            label_id = label_cache[label_key]
            log_message(f"The label ‘{label_name}’ ({planka_color}) is already in the cache, use the ID {label_id}")
        else:
            new_label = create_label(token, board_id, label_name, planka_color)
            if not new_label:
                log_message(f"Label creation error: {label_name} ({planka_color})")
                continue

            label_id = new_label["id"]
            label_cache[label_key] = label_id

        if not add_label_to_card(token, card_id_planka, label_id):
            log_message(f"Failed to bind label '{label_name}' ({planka_color}) to a card")
        else:
            log_message(f"The label '{label_name if label_name else '(no name)'}' ({planka_color}) has been added")

# Main migration function (minimum time.sleep parameter recommended by api Trello ≥ 0.1. You can change it to speed up migration)
def migrate_workspaces():
    token = get_token()
    log_message(f"Received bearer token {token} Planka, successful authorisation on the server")
    trello_counts = count_trello_items()
    
    log_message("\nDiscovered elements in Trello:")
    log_message(f"Total workspaces found in Trello: {trello_counts['workspaces']}")
    log_message(f"Total boards found on Trello: {trello_counts['boards']}")
    log_message(f"Total lists found in Trello: {trello_counts['lists']}")
    log_message(f"Total cards found in Trello: {trello_counts['cards']}")
    log_message(f"Total attachments found in Trello: {trello_counts['attachments']}")
    log_message(f"Total comments found in Trello: {trello_counts['comments']}")

    workspaces = get_workspaces() 
    count_workspaces = len(workspaces)
    count_boards = count_lists = count_cards = count_attachments = count_comments = 0

    for ws in reversed(workspaces):
        log_message(f"migrate workspaces: {ws['displayName']}")  # migrate workspaces
        project = create_project(token, ws['displayName'])
        time.sleep(0.25)
        
        boards = get_boards(ws['id']) # board migration
        count_boards += len(boards)
        for board in reversed(boards):
            log_message(f"board migration: {board['name']}")
            board_planka = create_board(token, project['id'], board['name'])
            time.sleep(0.25)
            try:
                lists = get_lists(board['id']) # list migration
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    log_message(f"A deleted board was missed: {board['name']} ({board['id']})")
                    continue
                else:
                    raise
            count_lists += len(lists)
            for lst in reversed(lists):
                log_message(f"list migration: {lst['name']}")
                list_planka = create_list(token, board_planka['id'], lst['name'])
                time.sleep(0.25)
                
                cards = get_cards(lst['id'])  # card migration
                count_cards += len(cards)
                for card in reversed(cards):
                    due_date = card.get('due')
                    completed = card.get('dueComplete', False)
                    card_planka = create_card(token, list_planka['id'], card['name'], card.get('desc', ''), due_date, completed)
                    time.sleep(0.25)

                    # attachment migration
                    attachments = get_card_attachments(card['id'], APIKEY, APITOKEN)
                    count_attachments += len(attachments)
                    migrate_attachments(token, card_planka['id'], card['id'])
                    
                    # label migration
                    migrate_card_labels(token, board_planka['id'], card_planka['id'], card)
                    
                    # migration of checklists (tasks)
                    checklists = get_card_checklists(card['id'])
                    for checklist in reversed(checklists):
                        for item in reversed(checklist["checkItems"]):
                            is_completed = item["state"] == "complete"
                            create_task(token, card_planka['id'], item["name"], is_completed)
                            time.sleep(0.25)

                    # comment migration
                    comments = get_card_comments(card['id'])
                    count_comments += len(comments)
                    for comment in reversed(comments):
                        log_message(f"Adding a comment to a card: {comment['data']['text'][:30]}...")
                        add_comment(
                            token,
                            card_planka['id'],
                            comment['data']['text'],
                            comment['memberCreator']['fullName'],
                            comment['memberCreator']['username'],
                            comment['date']
                        )
                        time.sleep(0.25)
    
    # Display the migration report
    log_message("\nMigration complete!")
    log_message(f"Total workspaces: {trello_counts['workspaces']} found in Trello, {count_workspaces} transferred to Planka")
    log_message(f"Total board: {trello_counts['boards']} found in Trello, {count_boards} transferred to Planka")
    log_message(f"Total lists: {trello_counts['lists']} found in Trello, {count_lists} transferred to Planka")
    log_message(f"Total cards: {trello_counts['cards']} found in Trello, {count_cards} transferred to Planka")
    log_message(f"Total attachments: {trello_counts['attachments']} found in Trello, {count_attachments} transferred to Planka")
    log_message(f"Total comments: {trello_counts['comments']} found in Trello, {count_comments} transferred to Plankaa")

    # Shows a warning if something has not been transferred
    if (trello_counts['cards'] > count_cards or 
        trello_counts['attachments'] > count_attachments or 
        trello_counts['comments'] > count_comments):
        log_message("WARNING: Not all data has been migrated! Check the log for errors")