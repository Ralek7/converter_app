# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.', './core'],  # Ruta a módulos personalizados
    binaries=[],
    datas=[
        ('secrets/secrets.ini', 'secrets'),
        ('core/*.py', 'core'),
        ('output/jira_issues', 'output/jira_issues'),  # Nueva estructura
        ('output/test_cases', 'output/test_cases'),
        ('output/features', 'output/features')
    ],

    hiddenimports=[
        'configparser',
        'requests',
        'urllib3',
        'tkinter',
        'logging',
        'pathlib',
        'json',
        'textwrap',
        'unicodedata',
        'jiraExtractor',
        'valueEdgeExtractor',
        'gherkinConverter',
        'time'  # Añadir si se usa throttling
    ]

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DICAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Deshabilitar UPX para evitar antivirus
    cipher=block_cipher,  # Usar cifrado
    noarchive=True  # Evitar que se extraiga el código fácilmente
    runtime_tmpdir='.',
    console=True,  # Cambiar a True para debug
    icon='icon.ico'  # Opcional
)