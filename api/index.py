import os
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devbhoomi.settings')
os.environ.setdefault('VERCEL', '1')
os.environ.setdefault('DB_PATH', '/tmp/devbhoomi.sqlite3')

import django
from django.core.management import call_command

# Vercel uses an ephemeral filesystem, so the SQLite file must live in /tmp.
# Create the file path and apply migrations at startup so the tables exist.
target_db = Path(os.environ['DB_PATH'])
target_db.parent.mkdir(parents=True, exist_ok=True)
target_db.touch(exist_ok=True)

django.setup()
call_command('migrate', interactive=False, verbosity=0)

from devbhoomi.wsgi import application

app = application
