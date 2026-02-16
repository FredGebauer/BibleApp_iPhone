from setuptools import setup

APP = ['BibleAppIP.py']

DATA_FILES = [
    ('templates', ['templates/index.html']),
    ('static', ['static/style.css', 'static/script.js']),
    ('', ['interpretations.json'])
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['flask', 'requests'],
    'iconfile': 'app.icns',
    'includes': ['server', 'bible_lookup']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
