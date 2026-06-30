import os
import sys
import getpass
import subprocess
import configparser
from pathlib import Path

def get_real_user():
    """Get the actual user who invoked sudo, not the root user."""
    return os.environ.get('SUDO_USER') or getpass.getuser()

def main():
    print("==============================================")
    print(" Synora Studio - Systemd Service Configurator")
    print("==============================================\n")
    
    if os.name == 'nt':
        print("❌ Error: This script configures 'systemd' and is intended for Linux only.")
        sys.exit(1)

    if os.geteuid() != 0:
        print("❌ Error: You must run this script as root to write to /etc/systemd/system/.")
        print("Please run this command instead:")
        print("  sudo python3 scripts/install_services.py")
        sys.exit(1)

    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    user = get_real_user()
    python_path = os.path.join(repo_dir, "venv", "bin", "python")

    print(f"Detected Installation Directory: {repo_dir}")
    print(f"Detected Operating User: {user}")

    if not os.path.exists(python_path):
        print(f"\n⚠️ Warning: Virtual environment python not found at {python_path}")
        print("Falling back to system python (not recommended for production).")
        python_path = sys.executable
    else:
        print(f"Using Virtual Environment: {python_path}")

    # Read the actual port configured for the Core API
    core_config_path = os.path.join(repo_dir, "core", "config.ini")
    core_port = "5051"
    if os.path.exists(core_config_path):
        config = configparser.ConfigParser()
        config.read(core_config_path)
        if config.has_option("Network", "port"):
            core_port = config.get("Network", "port")

    # Dynamically generate Core Service Content
    core_service_content = f"""[Unit]
Description=Synora Studio Core ML API
After=network.target

[Service]
User={user}
WorkingDirectory={repo_dir}
ExecStart={python_path} -m core.core
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

    # Dynamically generate Web Service Content
    web_service_content = f"""[Unit]
Description=Synora Studio Web UI
After=network.target synora-core.service

[Service]
User={user}
WorkingDirectory={repo_dir}
Environment="CORE_API_URL=http://localhost:{core_port}/api/remove"
ExecStart={python_path} -m web.web
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

    core_service_path = "/etc/systemd/system/synora-core.service"
    web_service_path = "/etc/systemd/system/synora-web.service"

    print("\nGenerating systemd service files...")
    
    with open(core_service_path, "w") as f:
        f.write(core_service_content)
    print(f"✅ Created: {core_service_path}")

    with open(web_service_path, "w") as f:
        f.write(web_service_content)
    print(f"✅ Created: {web_service_path}")

    print("\nReloading systemd daemon...")
    subprocess.run(["systemctl", "daemon-reload"], check=True)

    print("Enabling services to start on boot...")
    subprocess.run(["systemctl", "enable", "synora-core"], check=True)
    subprocess.run(["systemctl", "enable", "synora-web"], check=True)

    print("Starting services...")
    subprocess.run(["systemctl", "start", "synora-core"], check=True)
    subprocess.run(["systemctl", "start", "synora-web"], check=True)

    print("\n🎉 Installation Complete! Your services are now running in the background.")
    print("To check their status, use:")
    print("  sudo systemctl status synora-core")
    print("  sudo systemctl status synora-web")
    print("\nTo view live logs, use:")
    print("  sudo journalctl -u synora-core -f")
    print("  sudo journalctl -u synora-web -f")

if __name__ == "__main__":
    main()
