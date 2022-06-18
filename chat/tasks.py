class StartupTasks():
    is_running_as_server = False

    @classmethod
    def run(cls):
        cls.clear_current_users()

    @classmethod
    def run_only_in_server(cls):
        if cls.is_running_as_server:
            cls.run()

    @classmethod
    def clear_current_users(cls):
        from .models import UserChannelSesion
        UserChannelSesion.objects.all().delete()
