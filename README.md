# Trello to Planka Migration Script

## Description
This script is designed to migrate data from Trello to [Planka](https://github.com/plankanban/planka). It automatically transfers workspaces, boards, lists, cards, comments, attachments, labels, and card covers from Trello to Planka while preserving structure and important details.

---

## Features
- Transfers Trello workspaces as projects in Planka.
- Transfers boards and lists from Trello to Planka.
- Transfers Trello cards while preserving completion status.
- Transfers tasks from Trello cards to Planka cards.
- Transfers comments with author, date, and timestamp.
- Transfers attachments with the original creation date added to the filename.
- Converts attachment filenames to Latin characters.
- Transfers labels and card covers.
- Logs all migration actions and errors in `log.txt`.
- Counts all transferred elements for verification.

---

## Project Structure
- `config.py` — stores Trello and Planka authentication details.
- `labels_planka.py` — matches Trello and Planka label colors.
- `main.py` — entry point (run `python main.py`).
- `migrators.py` — main migration functions.
- `planka_api.py` — handles Planka API interactions.
- `trello_api.py` — handles Trello API interactions.
- `utils.py` — utilities (logging, token validation, etc.).

---

## Installation & Execution
1. **Create a folder on your server** and clone the repository:
   ```sh
   git clone https://github.com/garpastyls/Trello_to_Planka_migration_script.git
   ```
2. **Create a virtual environment**:
   ```sh
   python3.11 -m venv venv
   ```
3. **Activate the virtual environment**:
   ```sh
   source venv/bin/activate
   ```
4. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
5. **Configure `config.py`** by adding Trello and Planka API keys (see below).
6. **Run the script**:
   ```sh
   python main.py
   ```
7. **Check `log.txt`** after execution.

---

## Getting Trello API Key & Token
1. Go to [Trello Power-Ups](https://trello.com/power-ups/admin).
2. Click "Enhancements" → "Create New".
3. Enter your organization details.
4. Click "Generate new API key" and save it in `config.py`.
5. Click "Manually generate token" and allow access. Save the token in `config.py`.

---

## Configuration (`config.py`)
```python
# Authentication data for Planka
PLANKA_URL = "https://planka.com/api"  # Keep /api at the end
USERNAME = "admin"
PASSWORD = "admin"

# Authentication data for Trello
TRELLO_URL = "https://api.trello.com/1/"
APIKEY = "your_trello_api_key"
APITOKEN = "your_trello_api_token"
```

---

## Dependencies
All required libraries are listed in `requirements.txt`:
```txt
requests
unidecode
datetime
pytz
tqdm
```
> **Note:** `urllib.parse`, `os`, and `time` are included in Python's standard library.

---

## Script Behavior & Customization
- Comments include a signature:
  `"Imported comment from Trello, originally posted by [Author] [Username] [Date]"`
- Attachments have timestamps added to their filenames (`created_at_16-12-2024_13-18`).
- You can change the timezone in `planka_api.py` (default: `Europe/Moscow`).
- The default request delay is `0.25 sec` (can be reduced to `0.1 sec` for large migrations).

---

## Potential Issues & Errors
- **Error 413: `Request Entity Too Large` in Planka**
  Solution: Increase `client_max_body_size` in your `nginx` configuration.
- **Board backgrounds from Trello are not migrated**
  Planka assigns backgrounds to projects, not individual boards.
- **Images in comments may not display**
  Attachments are migrated, but Planka does not support embedded images in comments.
- **Attachments that are links will not migrate**
  Trello allows links as attachments, but Planka does not support this.
- **Duplicated Trello cards may lose comments**
  Trello does not duplicate comments when copying a card, causing API issues.

---

## Not realised
- **Migration of participants**  
- **Migration of archival elements (cards, boards)**  

---

## License
This project is released under the **MIT** license.

---

## Migration Summary
After a successful migration, `log.txt` will contain a summary:
```sh
Migration completed!
Total workspaces: 2 found in Trello, 2 migrated to Planka
Total boards: 11 found in Trello, 11 migrated to Planka
...
```
If the numbers do not match, check `log.txt` for errors using the keyword "Error".

---

### For any issues or questions, open an issue in the repository!

### 💡If you find this project useful, you can support my work — even a small donation makes a difference
- **Crypto donation: USDT (TRC20):** `TCECqH8ZxXGCQuWZeto1nV9nawbeeV4fG8`
- **Crypto donation: Bitcoin (BTC):** `bc1q3lvprzayxd3qulk0epk5dh58zx36mfev76wj30`
- **Crypto donation: Ethereum (ETH):** `0x80DbC00Fd91bAb3D4FE6E6441Dae0719e6bF5c9e`
- **International card (Visa/Mastercard):**  
[https://www.donationalerts.com/r/johngear](https://www.donationalerts.com/r/johngear)
