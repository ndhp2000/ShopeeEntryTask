from django.apps import AppConfig


class EventManagerAppConfig(AppConfig):
    name = 'event_manager_app'

    def ready(self):
        print("STARTING...")
        from .models import UsersModel
        from .models import SessionsModel
        UsersModel.objects.cache_all_username()
        SessionsModel.objects.cache_all_session()
        print("CACHE READY")
