# ==================================================================
# File: scripts/cleanup.py
# Description: 
# ==================================================================

import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Clutter to delete
FILES_TO_DELETE = [
    ".editorconfig",
    ".dockerignore",
    ".markdownlint.yaml",
    "pytest.ini",
    "tests",
    "rembg.py",
    "scripts/run_web.py",
    "scripts/run_headless.py",
    "api",
    "headless/app.py",
    "headless/cli.py"
]

# 2. Folders to create
FOLDERS_TO_CREATE = [
    "core",
    "headless"
]

# 3. Files to move
FILES_TO_MOVE = {
    # Core (Model)
    "rembg/bg.py": "core/bg.py",
    "rembg/session_factory.py": "core/session_factory.py",
    "rembg/sessions": "core/sessions",
    "rembg/__init__.py": "core/__init__.py",
    # Headless (Controller)
    "rembg/cli.py": "headless/cli.py",
    "rembg/commands": "headless/commands"
}

def replace_in_file(filepath, search, replace):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace(search, replace)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)

def restructure_core_web():
    print("\nMigrating Core and Web to Single-File Root Architecture...")
    
    # Core Migration
    core_main = os.path.join(ROOT_DIR, "core", "core_main")
    os.makedirs(core_main, exist_ok=True)
    
    core_files_to_move = ["bg.py", "server.py", "session_factory.py", "sessions", "__init__.py"]
    for f in core_files_to_move:
        src = os.path.join(ROOT_DIR, "core", f)
        dest = os.path.join(core_main, f)
        if os.path.exists(src) and not os.path.exists(dest):
            try:
                shutil.move(src, dest)
                print(f"Moved {src} to {dest}")
            except Exception as e:
                print(f"Error moving {src}: {e}")

    # Web Migration
    web_main = os.path.join(ROOT_DIR, "web", "web_main")
    os.makedirs(web_main, exist_ok=True)

    web_files_to_move = ["app.py", "i18n.py"]
    for f in web_files_to_move:
        src = os.path.join(ROOT_DIR, "web", f)
        dest = os.path.join(web_main, f)
        if os.path.exists(src) and not os.path.exists(dest):
            try:
                shutil.move(src, dest)
                print(f"Moved {src} to {dest}")
            except Exception as e:
                print(f"Error moving {src}: {e}")

    print("Fixing Internal Imports Across Extracted Modules...")
    
    # 1. Update headless/hl_main/app.py
    hl_app = os.path.join(ROOT_DIR, "headless", "hl_main", "app.py")
    replace_in_file(hl_app, "from core.bg import remove", "from core.core_main.bg import remove")
    replace_in_file(hl_app, "from core.session_factory", "from core.core_main.session_factory")
    replace_in_file(hl_app, "from core.sessions", "from core.core_main.sessions")

    # 2. Update web/web_main/app.py
    web_app_path = os.path.join(web_main, "app.py")
    replace_in_file(web_app_path, "from web.i18n", "from web.web_main.i18n")
    replace_in_file(web_app_path, "from core.bg", "from core.core_main.bg")

    # 3. Update headless commands (they import from core!)
    commands_dir = os.path.join(ROOT_DIR, "headless", "commands")
    if os.path.exists(commands_dir):
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                filepath = os.path.join(commands_dir, filename)
                replace_in_file(filepath, "from core.bg", "from core.core_main.bg")
                replace_in_file(filepath, "from core.session_factory", "from core.core_main.session_factory")
                replace_in_file(filepath, "from core.sessions", "from core.core_main.sessions")

def cleanup():
    print("Starting Extreme MVC Restructuring...")
    
    # Delete clutter
    for file_path in FILES_TO_DELETE:
        full_path = os.path.join(ROOT_DIR, file_path)
        if os.path.exists(full_path):
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
                print(f"Deleted clutter: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
                
    # Create new architectural folders
    # 1. Obsolete CI/CD and Installer files
    obsolete_paths = [
        os.path.join(ROOT_DIR, "rembg.py"),
        os.path.join(ROOT_DIR, "run_scripts"),
        os.path.join(ROOT_DIR, ".editorconfig"),
        os.path.join(ROOT_DIR, "gradio_app.py"),
        os.path.join(ROOT_DIR, "Dockerfile"),
        os.path.join(ROOT_DIR, "Dockerfile_nvidia_cuda_cudnn_gpu"),
        os.path.join(ROOT_DIR, "rembg.spec"),
        os.path.join(ROOT_DIR, ".github", "ISSUE_TEMPLATE"),
        os.path.join(ROOT_DIR, ".github", "workflows", "publish_pypi.yml"),
        os.path.join(ROOT_DIR, ".github", "workflows", "windows_installer.yml"),
        os.path.join(ROOT_DIR, ".github", "workflows", "close_inactive_issues.yml"),
        os.path.join(ROOT_DIR, "build_scripts"),
    ]
    
    for item in obsolete_paths:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                print(f"Deleted obsolete item: {item}")
            except Exception as e:
                print(f"Failed to delete {item}: {e}")

    for folder in FOLDERS_TO_CREATE:
        folder_path = os.path.join(ROOT_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"Ensured folder exists: {folder}/")

    # Move files to core and headless
    for src, dest in FILES_TO_MOVE.items():
        src_path = os.path.join(ROOT_DIR, src)
        dest_path = os.path.join(ROOT_DIR, dest)
        if os.path.exists(src_path):
            try:
                shutil.move(src_path, dest_path)
                print(f"Moved: {src} -> {dest}")
            except Exception as e:
                print(f"Failed to move {src}: {e}")

    # Remove original rembg folder if empty
    rembg_path = os.path.join(ROOT_DIR, "rembg")
    if os.path.exists(rembg_path):
        try:
            shutil.rmtree(rembg_path)
            print("Deleted old rembg/ wrapper directory.")
        except Exception as e:
            print(f"Could not delete rembg/: {e}")

    # FIX IMPORTS AFTER MOVE
    print("Fixing Internal Imports...")
    
    # Fix web imports
    web_app = os.path.join(ROOT_DIR, "web", "app.py")
    replace_in_file(web_app, "from rembg import remove", "from core.bg import remove")
    
    # Fix headless CLI imports
    cli_py = os.path.join(ROOT_DIR, "headless", "cli.py")
    replace_in_file(cli_py, "from .commands import", "from headless.commands import")
    
    # Fix headless commands relative imports
    commands_dir = os.path.join(ROOT_DIR, "headless", "commands")
    if os.path.exists(commands_dir):
        for filename in os.listdir(commands_dir):
            if filename.endswith(".py"):
                filepath = os.path.join(commands_dir, filename)
                replace_in_file(filepath, "from ..bg", "from core.bg")
                replace_in_file(filepath, "from ..session_factory", "from core.session_factory")
                replace_in_file(filepath, "from ..sessions", "from core.sessions")
                
    restructure_core_web()
    print("\nExtreme MVC Restructuring Complete!")

if __name__ == "__main__":
    cleanup()
