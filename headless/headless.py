import sys
import os

try:
    from headless.hl_main.app import app
except ImportError:
    pass

def main():
    """
    Unified entry point for the Headless architecture.
    Routes between the Public API and the Terminal CLI.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # Start API Server
        try:
            import uvicorn
            from headless.hl_main.app import app
        except ImportError:
            print("API dependencies not found. Run: pip install uvicorn fastapi")
            sys.exit(1)
            
        port = int(os.environ.get("PORT", 5052))
        print(f"Starting Synora Studio Headless API on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        # Pass remaining commands to CLI
        from headless.hl_main.cli import main as cli_main
        cli_main()

if __name__ == "__main__":
    main()
