from django.apps import AppConfig
# from django.db.models.signals import post_delete, post_save, pre_save


class NotesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notes'

    # def ready(self) -> None:
    #     from .models import Note
    #     from .signals import create_markdown_file, delete_markdown_file
    #     pre_save.connect(delete_markdown_file, sender=Note, dispatch_uid="delete_markdown_file_pre_save")
    #     post_save.connect(create_markdown_file, sender=Note, dispatch_uid="create_markdown_file")
    #     post_delete.connect(delete_markdown_file, sender=Note, dispatch_uid="delete_markdown_file_post_delete")
    #     return super().ready()
