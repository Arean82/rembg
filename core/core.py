# ==================================================================
# File: core/core.py
# Description: 
# ==================================================================

import sys
import os
import configparser

def get_config_port(section, key, default_port):
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    if os.path.exists(config_path):
        config.read(config_path)
        if config.has_section(section) and config.has_option(section, key):
            try:
                return int(config.get(section, key))
            except ValueError:
                pass
    return int(os.environ.get("PORT", default_port))

def main():
    """
    Unified entry point for the Core ML Engine.
    """
    try:
        import core.core_main.server as server
    except ImportError as e:
        print(f"Error loading Core Engine: {e}")
        print("Please ensure you have run the cleanup script and installed dependencies.")
        sys.exit(1)
        
    port = get_config_port('Network', 'port', 5051)
    print(f"Starting Synora Studio Core ML Engine on port {port}...")
    server.app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
