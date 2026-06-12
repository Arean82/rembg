import sys
import os

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
        
    port = int(os.environ.get("PORT", 5051))
    print(f"Starting Synora Studio Core ML Engine on port {port}...")
    server.app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
