# ==================================================================
# File: scripts/generate_locales.py
# Description: 
# ==================================================================

import os
import subprocess
import sys

try:
    import polib
    from deep_translator import GoogleTranslator
except ImportError:
    print("Please install requirements: pip install polib deep-translator Babel")
    sys.exit(1)

TARGET_LANGUAGES = ["es", "fr", "de", "zh", "ja"]
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BABEL_CFG = os.path.join(ROOT_DIR, "babel.cfg")
POT_FILE = os.path.join(ROOT_DIR, "messages.pot")
TRANSLATIONS_DIR = os.path.join(ROOT_DIR, "web", "translations")

def run_cmd(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, cwd=ROOT_DIR, shell=True, check=True)

def main():
    pybabel_cmd = f'"{sys.executable}" -c "from babel.messages.frontend import main; main()"'
    
    print("--- 1. Extracting Text to messages.pot ---")
    run_cmd(f"{pybabel_cmd} extract -F {BABEL_CFG} -o {POT_FILE} web")

    print(f"--- 2. Initializing or Updating Languages ---")
    for lang in TARGET_LANGUAGES:
        lang_dir = os.path.join(TRANSLATIONS_DIR, lang)
        if not os.path.exists(lang_dir):
            print(f"Initializing new language: {lang}")
            subprocess.run(f"{pybabel_cmd} init -i {POT_FILE} -d {TRANSLATIONS_DIR} -l {lang}", cwd=ROOT_DIR, shell=True)
            
    print("Updating all languages with latest text...")
    run_cmd(f"{pybabel_cmd} update -i {POT_FILE} -d {TRANSLATIONS_DIR}")

    print("--- 3. Auto-Translating via Deep-Translator ---")
    for lang in TARGET_LANGUAGES:
        po_file_path = os.path.join(TRANSLATIONS_DIR, lang, "LC_MESSAGES", "messages.po")
        if not os.path.exists(po_file_path):
            continue
            
        print(f"Translating {lang}...")
        po = polib.pofile(po_file_path)
        
        # Determine language code for Google Translate (e.g. zh -> zh-CN)
        gt_lang = lang
        if lang == 'zh':
            gt_lang = 'zh-CN'
            
        translator = GoogleTranslator(source='en', target=gt_lang)
        changed = False
        
        for entry in po:
            if not entry.msgstr: # Only translate empty strings
                try:
                    translation = translator.translate(entry.msgid)
                    entry.msgstr = translation
                    changed = True
                    print(f"  Translated [{lang}]: '{entry.msgid}' -> '{translation}'")
                except Exception as e:
                    print(f"  Error translating '{entry.msgid}': {e}")
                    
        if changed:
            po.save(po_file_path)

    print("--- 4. Compiling Translations to binary .mo ---")
    run_cmd(f"{pybabel_cmd} compile -d {TRANSLATIONS_DIR}")
    
    print("--- Locale Generation Complete! ---")

if __name__ == "__main__":
    main()
