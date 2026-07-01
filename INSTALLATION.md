# Installation Manual

Follow these steps to set up the Synora Studio Image Background Remover for local development.

## 1. Prerequisites
- Python 3.9 to 3.12 is recommended.
- Ensure `pip` is up to date.

## 2. Virtual Environment Setup
It is highly recommended to isolate your dependencies using a virtual environment.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies
Install the required packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

*(Note: The machine learning models (like `u2net`) are not downloaded via pip. The application will automatically download them the very first time you process an image.)*

## 4. Configuration
Open the `config.ini` file in the root directory. 
- Ensure `port = 5050` (or change it if that port is in use).
- For local development, leave `db_uri = sqlite:///storage/db/synora_local.db`.
- To test the "Guest" tier features, set `simulate_logged_in_user = false`.
- To test the "Logged-in" tier features, set `simulate_logged_in_user = true`.

## 5. Run the Application
Start the unified application:

```bash
python app.py
```

The terminal will confirm the server is running and the background cleanup scheduler has started.
Navigate to `http://localhost:5050` to begin.
