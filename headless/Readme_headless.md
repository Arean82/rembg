# Synora Studio BG Remover - Headless Server

The **Headless Server** is the public-facing FastAPI application. It exposes a fast, modern REST API with Swagger documentation. It runs on Port `5052`.

---

## 🚀 Production Deployment

There are two primary ways to deploy the API in production: using Uvicorn in a Python Virtual Environment, or using a Compiled PyInstaller Binary.

### Method A: Standard Python Deployment (Uvicorn + Systemd)
If you are running the raw Python code on a Linux server, you must use **Uvicorn** and **Systemd** to keep it alive forever.

#### 1. Setup the Project
```bash
cd /var/www
git clone https://github.com/Arean82/synorastudio_bg_remove.git
cd synorastudio_bg_remove
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install uvicorn
```

#### 2. Create the Systemd Service
Create `/etc/systemd/system/synora-bg-remove-headless.service`:
```ini
[Unit]
Description=Synora Studio Headless FastAPI
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/synorastudio_bg_remove
ExecStart=/var/www/synorastudio_bg_remove/venv/bin/uvicorn headless.headless:app --host 127.0.0.1 --port 5052
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable synora-bg-remove-headless
sudo systemctl start synora-bg-remove-headless
sudo journalctl -u synora-bg-remove-headless -f
```

### Method B: PyInstaller Standalone Binary Deployment
If you don't want to deal with Python environments or Uvicorn on your server, compile the API into a standalone binary.

#### 1. Build the Binary
```bash
pip install pyinstaller
# For a single portable file:
pyinstaller synora-headless-onefile.spec
# For a faster, uncompressed folder:
pyinstaller synora-headless-onedir.spec
```

#### 2. Deploy as a Linux Systemd Service
Create the exact same `systemd` service as Method A, but change the `ExecStart` path to point directly to your compiled binary:
```ini
ExecStart=/var/www/synorastudio_bg_remove/dist/synora-headless-onefile/synora-headless-onefile_rmbg
```

#### 3. Deploy as a Windows Background Service (NSSM)
If you are deploying on Windows and want it to run invisibly in the background across reboots, use [NSSM](http://nssm.cc/):
1. Download NSSM and extract it.
2. Open Administrator PowerShell and run:
```powershell
nssm install SynoraHeadless "C:\path\to\dist\synora-headless-onefile\synora-headless-onefile_rmbg.exe"
nssm set SynoraHeadless AppDirectory "C:\path\to\dist\synora-headless-onefile"
nssm start SynoraHeadless
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


