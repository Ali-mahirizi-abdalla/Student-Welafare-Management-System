from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

class BackupStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = os.path.join(settings.BASE_DIR, 'backups')
        super().__init__(*args, **kwargs)
