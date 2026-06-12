import os

def create_spec(component_name, entry_point, hidden_imports, datas, build_type):
    folder_name = f"synora-{component_name}-{build_type}"
    file_name = f"synora-{component_name}-{build_type}_rmbg"
    spec_filename = f"{folder_name}.spec"
    
    datas_str = ",\n        ".join([f"('{src}', '{dest}')" for src, dest in datas])
    if datas_str:
        datas_str = f"[{datas_str}]"
    else:
        datas_str = "[]"
        
    hidden_imports_str = ",\n        ".join([f"'{imp}'" for imp in hidden_imports])
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['{entry_point}'],
    pathex=[],
    binaries=[],
    datas={datas_str},
    hiddenimports=[
        {hidden_imports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

"""
    if build_type == "onefile":
        # ONEFILE MODE
        spec_content += f"""
# Alter DISTPATH to place the onefile inside its own directory
DISTPATH = os.path.join(DISTPATH, '{folder_name}')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{file_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    else:
        # ONEDIR MODE
        spec_content += f"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{file_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{folder_name}'
)
"""
    
    with open(spec_filename, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print(f"Generated: {spec_filename}")

def main():
    # 1. CORE
    core_hidden = ['core', 'core.core_main.server', 'core.core_main.bg', 'core.core_main.session_factory']
    create_spec("core", "core/core.py", core_hidden, [], "onefile")
    create_spec("core", "core/core.py", core_hidden, [], "onedir")

    # 2. HEADLESS
    headless_hidden = ['headless', 'headless.hl_main.app', 'headless.hl_main.cli', 'uvicorn']
    create_spec("headless", "headless/headless.py", headless_hidden, [], "onefile")
    create_spec("headless", "headless/headless.py", headless_hidden, [], "onedir")

    # 3. WEB
    web_hidden = ['web', 'web.web_main.app', 'web.web_main.i18n', 'flask_babel']
    web_datas = [('web/templates', 'web/templates'), ('web/static', 'web/static'), ('web/translations', 'web/translations')]
    create_spec("web", "web/web.py", web_hidden, web_datas, "onefile")
    create_spec("web", "web/web.py", web_hidden, web_datas, "onedir")

if __name__ == "__main__":
    main()
