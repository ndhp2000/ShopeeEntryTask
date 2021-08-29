import logging

from django.apps import AppConfig

# Get an instance of a logger
logger = logging.getLogger('django')


class EventManagerAppConfig(AppConfig):
    name = 'event_manager_app'

    # def ready(self):
    #     logger.info("START LOAD DATA TO CACHE")
    #     from .models import UsersModel
    #     from .models import SessionsModel
    #     UsersModel.objects.cache_all_username()
    #     SessionsModel.objects.cache_all_session()
    #     logger.info("DONE LOAD DATA TO CACHE")
