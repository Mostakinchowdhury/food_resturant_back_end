# utils.py
import os
import uuid
from datetime import datetime

def get_upload_to(folder_name):
    def generate_file_path(instance, filename):   # Django expects (instance, filename)
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        ext = filename.split('.')[-1]
        unique_name = f"{uuid.uuid4().hex}.{ext}"

        folder_path = os.path.join(folder_name, year, month, day)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        return os.path.join(folder_name, year, month, day, unique_name)

    return generate_file_path

def generate_file_path(instance, filename, folder_name='uploads'):
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    folder_path = os.path.join(folder_name, year, month, day)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return os.path.join(folder_name, year, month, day, unique_name)
