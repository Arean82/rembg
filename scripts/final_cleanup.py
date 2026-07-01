import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cleanup_obsolete_files():
    print("Starting cleanup of obsolete architecture files...")
    
    # Files to delete
    files_to_delete = [
        "synora-core-onedir.spec",
        "synora-core-onefile.spec",
        "synora-headless-onedir.spec",
        "synora-headless-onefile.spec",
        "synora-web-onedir.spec",
        "synora-web-onefile.spec",
        "web/web.py",
        "core/core.py"
    ]
    
    # Directories to delete
    dirs_to_delete = [
        "headless",
        "build",
        "dist"
    ]
    
    for f in files_to_delete:
        path = os.path.join(ROOT_DIR, f)
        if os.path.exists(path):
            os.remove(path)
            print(f"Deleted file: {f}")
            
    for d in dirs_to_delete:
        path = os.path.join(ROOT_DIR, d)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"Deleted directory: {d}")
            
    print("Cleanup complete. Your repository is now fully streamlined for the unified API architecture.")

if __name__ == "__main__":
    cleanup_obsolete_files()
