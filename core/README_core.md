# Synora Studio BG Remover - Core Engine

The **Core Engine** is the deeply optimized, highly scalable ML backend that powers Synora Studio. It runs internally on Port `5051` and processes image bytes directly.

---

## 🚀 Production Deployment

There are two primary ways to deploy the engine in production: using a Standard Python Virtual Environment, or using a Compiled PyInstaller Binary.

### Method A: Standard Python Deployment (Linux Systemd)
If you are running the raw Python code on a Linux server, you should use `systemd` to keep it alive forever.

#### 1. Create the Systemd Service
Create `/etc/systemd/system/synora-bg-remove-core.service`:
```ini
[Unit]
Description=Synora Studio Core ML Engine
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/synorastudio_bg_remove
ExecStart=/var/www/synorastudio_bg_remove/venv/bin/python core/core.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### 2. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable synora-bg-remove-core
sudo systemctl start synora-bg-remove-core
sudo journalctl -u synora-bg-remove-core -f
```

### Method B: PyInstaller Standalone Binary Deployment
If you don't want to deal with Python environments on your production server, you can compile the engine into a standalone binary.

#### 1. Build the Binary
```bash
pip install pyinstaller
# For a single portable file:
pyinstaller synora-core-onefile.spec
# For a faster, uncompressed folder:
pyinstaller synora-core-onedir.spec
```

#### 2. Deploy as a Linux Systemd Service
Create the exact same `systemd` service as Method A, but change the `ExecStart` path to point directly to your compiled binary:
```ini
ExecStart=/var/www/synorastudio_bg_remove/dist/synora-core-onefile/synora-core-onefile_rmbg
```

#### 3. Deploy as a Windows Background Service (NSSM)
If you are deploying on Windows and want it to run invisibly in the background across reboots, use [NSSM](http://nssm.cc/):
1. Download NSSM and extract it.
2. Open Administrator PowerShell and run:
```powershell
nssm install SynoraCore "C:\path\to\dist\synora-core-onefile\synora-core-onefile_rmbg.exe"
nssm set SynoraCore AppDirectory "C:\path\to\dist\synora-core-onefile"
nssm start SynoraCore
```

---

## Developer Mode (Local Execution)

If you are just developing locally, you do not need Systemd. You can install the Core Engine in "Editable Mode" so that changes to the Python files reflect instantly:

```bash
# 1. Move to your web directory
cd /var/www

# 2. Clone your code
git clone https://github.com/Arean82/synorastudio_bg_remove.git
cd synorastudio_bg_remove

# 3. Create and activate a virtual environment
pip install -e .
```

### How to Run Locally
To actually start the Core Engine on your personal computer, simply run the unified python file directly:
```bash
python core/core.py
```
*(It will start the server on Port 5051)*

### How to Update
Because you installed using the `-e` flag, Python links directly to this folder. To update the Core Engine to the newest version, simply pull the latest code. There is no need to reinstall!
```bash
git pull origin main
```

### How to Uninstall
If you want to completely remove the app and its dependencies from your python environment:
```bash
pip uninstall synorastudio-bg-remove
```



### ⚖️ Developer Installation vs. Production Services
**`pip install -e .` (Developer Mode)**
- Perfect for local development, testing, and using the terminal CLI.
- Runs in your active terminal. If you close the terminal, the application dies.

**Systemd Service (Production Mode)**
- Perfect for hosting the 24/7 background ML Engine.
- Runs invisibly in the background. If your server crashes or reboots, Systemd automatically starts the ML engine back up without you having to log in.
