import os
from django.conf import settings
from .models import Note
import errno


def remove_empty_folders(root):
    folders = list(os.walk(root))[1:]
    for folder in folders:
        if not folder[2]:
            try:
                os.rmdir(folder[0])
            except Exception as e:
                print(e)


def create_markdown_file(sender, instance, created, **kwargs):
    if created and sender == Note:
        media_root = settings.MEDIA_ROOT
        filename = f'{media_root}/user_{instance.created_by.id}/{instance.location}/{instance.title}.md'
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(filename, "w") as f:
            f.write(instance.text)


def delete_markdown_file(sender, instance, **kwargs):
    if sender == Note:
        media_root = settings.MEDIA_ROOT
        filename = f'{media_root}/user_{instance.created_by.id}/{instance.location}/{instance.title}.md'
        try:
            os.remove(filename)
        except OSError as exc:
            print(exc)

        remove_empty_folders(f'{media_root}/user_{instance.created_by.id}')
