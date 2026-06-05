import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devbhoomi.settings')

from devbhoomi.wsgi import application

app = application
