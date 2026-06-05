import os
import shutil
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devbhoomi.settings')

# Vercel runs from a read-only filesystem for the app bundle, so copy the
# bundled SQLite database into /tmp before Django opens it.
source_db = Path(__file__).resolve().parent.parent / 'db.sqlite3'
target_db = Path('/tmp/devbhoomi.sqlite3')
if source_db.exists() and not target_db.exists():
    target_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_db, target_db)
os.environ.setdefault('DB_PATH', str(target_db))
os.environ.setdefault('VERCEL', '1')

from devbhoomi.wsgi import application

app = application
