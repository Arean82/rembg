import threading
import time
from core.core_main.db import cleanup_expired_images

def run_scheduler(app):
    while True:
        try:
            cleanup_expired_images(app)
        except Exception as e:
            print(f"Scheduler Error: {e}")
        # Run every 5 minutes
        time.sleep(300)

def start_scheduler(app):
    thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
    thread.start()
    print("Background cleanup scheduler started.")
