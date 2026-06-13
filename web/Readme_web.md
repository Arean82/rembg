# Synora Studio BG Remover - Web UI

The **Web Frontend** is a fully functional, glassmorphic UI built in Flask that allows users to interact with Synora Studio directly from their browser. It runs on Port `5050`.

---

## 🚀 Production Deployment

There are two primary ways to deploy the Web UI in production: using a Standard Python Virtual Environment with WSGI, or using a Compiled PyInstaller Binary.

### Method A: Standard Python Deployment (WSGI)
Do **NOT** use `python web/web.py` in production. You must use a robust, multi-threaded production WSGI server.

#### 1. Setup WSGI (Waitress/Gunicorn)
**On Windows (Waitress):**
```powershell
pip install waitress
waitress-serve --port=5050 web.web:app
```
**On Linux (Gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5050 web.web:app
```

#### 2. Create the Systemd Service (Linux Only)
Create `/etc/systemd/system/synora-bg-remove-web.service`:
```ini
[Unit]
Description=Synora Studio Web UI (Gunicorn)
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/synorastudio_bg_remove
ExecStart=/var/www/synorastudio_bg_remove/venv/bin/gunicorn -w 4 -b 127.0.0.1:5050 web.web:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 3. Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable synora-bg-remove-web
sudo systemctl start synora-bg-remove-web
sudo journalctl -u synora-bg-remove-web -f
```

### Method B: PyInstaller Standalone Binary Deployment
If you don't want to deal with Python environments or WSGI, you can compile the Web UI into a standalone binary. I have provided a custom `.spec` file that perfectly embeds your HTML/CSS!

#### 1. Build the Binary
```bash
pip install pyinstaller
# For a single portable file:
pyinstaller synora-web-onefile.spec
# For a faster, uncompressed folder:
pyinstaller synora-web-onedir.spec
```

#### 2. Deploy as a Linux Systemd Service
Create the exact same `systemd` service as Method A, but change the `ExecStart` path to point directly to your compiled binary:
```ini
ExecStart=/var/www/synorastudio_bg_remove/dist/synora-web-onefile/synora-web-onefile_rmbg
```

#### 3. Deploy as a Windows Background Service (NSSM)
If you are deploying on Windows and want it to run invisibly in the background across reboots, use [NSSM](http://nssm.cc/):
1. Download NSSM and extract it.
2. Open Administrator PowerShell and run:
```powershell
nssm install SynoraWeb "C:\path\to\dist\synora-web-onefile\synora-web-onefile_rmbg.exe"
nssm set SynoraWeb AppDirectory "C:\path\to\dist\synora-web-onefile"
nssm start SynoraWeb
```

---

## 3. Nginx Configuration & SSL

If you want to expose both the Web UI and the Headless API to the internet on standard ports (80/443), Nginx is required.

Create an Nginx server block at `/etc/nginx/sites-available/synora`:

```nginx
server {
    server_name synora.yourdomain.com;

    # Route Web UI Traffic (Port 5050)
    location / {
        proxy_pass http://127.0.0.1:5050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Route Headless API Traffic (Port 5052)
    location /api/ {
        proxy_pass http://127.0.0.1:5052/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and install SSL via Certbot:
```bash
sudo ln -s /etc/nginx/sites-available/synora /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d synora.yourdomain.com
```

---

## Developer Mode (Local Execution)

If you are developing locally, you do not need Waitress, Gunicorn, Nginx, or Systemd. You can install the application in "Editable Mode" so that changes to the HTML and Python files reflect instantly:

```bash
pip install -e .
```



### How to Run Locally
To actually start the Web UI on your personal computer, simply run the unified python file directly:
```bash
python web/web.py
```
*(It will start the Flask server on Port 5050)*

### How to Update
Because you installed using the `-e` flag, Python links directly to this folder. To update the Web UI to the newest version, simply pull the latest code. There is no need to reinstall!
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
- Perfect for local development, UI testing, and using the terminal CLI.
- Runs in your active terminal. If you close the terminal, the application dies.
- Cannot handle thousands of simultaneous web requests (it runs single-threaded by default).

**Systemd Services + WSGI (Production Mode)**
- Perfect for hosting the Web app on a live internet server.
- Runs invisibly in the background. If your server crashes or reboots, Systemd automatically starts the web app back up.
- Uses tools like Waitress or Gunicorn to spin up dozens of simultaneous worker threads to handle massive web traffic without crashing.
