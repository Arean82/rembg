# Synora Studio BG Remover - Core Engine

The **Core Engine** is the deeply optimized, highly scalable ML backend that powers Synora Studio. It runs internally on Port `5051` and processes image bytes directly.

---

## Production Deployment (Linux)

To ensure the Core Engine stays alive in production, starts on boot, and automatically restarts if it crashes, you must deploy it as a Linux `systemd` service.

### 1. Create the Systemd Service
Create a new file at `/etc/systemd/system/synora-bg-remove-core.service`:

```ini
[Unit]
Description=Synora Studio Core ML Engine
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/rembg
# Replace with the path to your python binary or virtual environment
ExecStart=/path/to/venv/bin/python core/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start the Service
Reload the system daemon to detect the new file, then enable and start the engine:

```bash
sudo systemctl daemon-reload
sudo systemctl enable synora-bg-remove-core
sudo systemctl start synora-bg-remove-core
```

### 3. Check Status
You can monitor the ML engine logs in real-time by running:
```bash
sudo journalctl -u synora-bg-remove-core -f
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

### 📦 Building with PyInstaller
You can compile the Core Engine into a standalone `.exe` using PyInstaller. I have included a highly optimized `.spec` file that automatically bundles all necessary invisible background dependencies!

To build it:
```bash
pip install pyinstaller

# For a single portable .exe file:
pyinstaller synora-core-onefile.spec

# For a faster, uncompressed folder containing the .exe:
pyinstaller synora-core-onedir.spec
```
This generates a perfectly bundled portable `.exe` in your `dist/` folder that requires NO python installation!

### ⚖️ Developer Installation vs. Production Services
**`pip install -e .` (Developer Mode)**
- Perfect for local development, testing, and using the terminal CLI.
- Runs in your active terminal. If you close the terminal, the application dies.

**Systemd Service (Production Mode)**
- Perfect for hosting the 24/7 background ML Engine.
- Runs invisibly in the background. If your server crashes or reboots, Systemd automatically starts the ML engine back up without you having to log in.
