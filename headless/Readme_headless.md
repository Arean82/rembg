# Synora Studio BG Remover - Headless Server

The **Headless Server** is the public-facing FastAPI application. It exposes a fast, modern REST API with Swagger documentation. It runs on Port `5052`.

---

## 🚀 Detailed Production Deployment Guide (Linux)

When deploying to a production server (like an Ubuntu VPS), you do not just run the python file directly. If you do, it will crash when you close your SSH terminal! 

Instead, you use **Uvicorn** (a production server specifically designed to execute FastAPI `.py` files) and **Systemd** (Linux's built-in background manager) to keep it alive forever.

Here is the exact, step-by-step guide from scratch:

### Step 1: Setup the Project on the Server
First, download your code and set up an isolated Python environment so your dependencies don't break the server.
```bash
# 1. Move to your web directory
cd /var/www

# 2. Clone your code
git clone https://github.com/Arean82/synorastudio_bg_remove.git
cd synorastudio_bg_remove

# 3. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install the requirements and Uvicorn
pip install -r requirements.txt
pip install uvicorn
```

### Step 2: How Uvicorn executes your `.py` file
Uvicorn is a command-line tool. When you run `uvicorn headless.app:app`, Uvicorn does the following:
1. It looks for a folder named `headless/`.
2. It looks for a python file inside it named `app.py`.
3. It finds the FastAPI variable named `app` inside that file, and executes it on a massive, multi-threaded scale.

### Step 3: Create the Systemd Background Service
We want Linux to run that Uvicorn command automatically in the background.

Create a new file by typing:
```bash
sudo nano /etc/systemd/system/synora-bg-remove-headless.service
```

Paste this exact configuration into it:
```ini
[Unit]
Description=Synora Studio Headless FastAPI
After=network.target

[Service]
User=ubuntu
# This is the directory where your headless folder lives
WorkingDirectory=/var/www/synorastudio_bg_remove
# This tells Linux to use your virtual environment's uvicorn to run the .py file!
ExecStart=/var/www/synorastudio_bg_remove/venv/bin/uvicorn headless.headless:app --host 127.0.0.1 --port 5052
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
*(Save and exit Nano by pressing `CTRL+X`, then `Y`, then `Enter`)*

### Step 4: Turn it on!
Now tell Linux to load your new service and turn it on:
```bash
sudo systemctl daemon-reload
sudo systemctl enable synora-bg-remove-headless
sudo systemctl start synora-bg-remove-headless
```

Your Python file is now officially running as a professional, invisible daemon process in the background! 

### Step 5: Check if it's working
To see the live logs (errors, prints, and incoming traffic), run:
```bash
sudo journalctl -u synora-bg-remove-headless -f
```

---

## 💻 Developer Mode (Local Execution on your PC)

If you are just developing locally on Windows/Mac, you do NOT need Systemd or Uvicorn. You just run the file manually.

### 1. Install it
```bash
pip install -e .
```

### 2. How to Run Locally
To actually start the public API server on your personal computer, simply run the unified python file directly:
```bash
python headless/headless.py api
```
*(It will instantly start up on Port 5052)*

### 3. How to Update
Because you installed using the `-e` flag, Python links directly to this folder. To update the application to the newest version, simply pull the latest code. There is no need to reinstall!
```bash
git pull origin main
```

### 4. How to Uninstall
If you want to completely remove the app and its dependencies from your python environment:
```bash
pip uninstall synorastudio-bg-remove
```

### 📦 Building with PyInstaller
You can compile the API into a standalone `.exe` using PyInstaller. I have included an optimized `.spec` file that perfectly maps your Uvicorn routes!

To build it:
```bash
pip install pyinstaller

# For a single portable .exe file:
pyinstaller synora-headless-onefile.spec

# For a faster, uncompressed folder containing the .exe:
pyinstaller synora-headless-onedir.spec
```
This generates a perfectly bundled portable `.exe` in your `dist/` folder!
