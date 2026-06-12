import sys
import os

def main():
    """
    Unified entry point for the Web UI.
    """
    try:
        import web.web_main.app as web_app
    except ImportError as e:
        print(f"Error loading Web UI: {e}")
        print("Please ensure you have run the cleanup script and installed dependencies.")
        sys.exit(1)
        
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting Synora Studio Web UI on port {port}...")
    web_app.app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
