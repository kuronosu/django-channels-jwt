import sys
from django.apps import AppConfig

from chat.tasks import StartupTasks


class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

    def ready(self, *args, **kwargs):
        is_manage_py = any(arg.casefold().endswith("manage.py")
                           for arg in sys.argv)
        is_runserver = any(arg.casefold() == "runserver" for arg in sys.argv)

        if (is_manage_py and is_runserver) or (not is_manage_py):
            StartupTasks.is_running_as_server = True
