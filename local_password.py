# ローカルデバッグ用に個人URLをすべてその人の名前に

import os
import django
import re
import csv
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jbsl2.settings')
django.setup()

from app.models import Player

for p in Player.objects.all():
    p.hashurl = p.name
    p.save()