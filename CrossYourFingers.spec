# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\game\\game.py'],
    pathex=['c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder'],
    binaries=[],
    datas=[('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/tasks\\tasks.json', 'builder\\tasks'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\shared/theme\\styles.qss', 'shared\\theme'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\amazon.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\apple.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\google_play.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\microsoft.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\target.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\visa.json', 'builder\\data\\gift_cards'), ('c:\\Users\\Valued Customer\\Documents\\scammer_payback_game_builder\\builder/data/gift_cards\\walmart.json', 'builder\\data\\gift_cards')],
    hiddenimports=['shared.tasks.location_collection', 'shared.tasks.multiple_choice', 'shared.tasks.name_collection', 'shared.tasks.short_answer', 'shared.config', 'shared.theme.theme', 'shared.utils.close_button_blocker', 'shared.utils.keyboard_blocker', 'shared.utils.mouse_locker', 'shared.utils.sleep_blocker', 'shared.utils.security_monitor', 'shared.utils.logger', 'shared.utils.ui_keyboard', 'builder.gift_card'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CrossYourFingers',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
