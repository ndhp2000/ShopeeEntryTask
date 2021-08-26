import asyncio
import sys
import threading

from django.db import models, connection
from django.core.cache import cache
import logging

# Get an instance of a logger
logger = logging.getLogger('django')


class SessionsManager(models.Manager):

    def is_session_token_existed(self, session_token):
        if cache.get(('Sessions_Manager', 'session_token', session_token)):
            return True
        return False
        # return self.filter(session_token=session_token).exists()

    def is_refresh_token_existed(self, refresh_token):
        if cache.get(('Sessions_Manager', 'refresh_token', refresh_token)):
            return True
        return False
        # return self.filter(refresh_token=refresh_token).exists()

    def __create_or_update_token(self, session_token, refresh_token, expired_time, user_id):
        self.update_or_create(user_id=user_id, defaults={'session_token': session_token, 'refresh_token': refresh_token,
                                                         'expired_time': expired_time})
        # connection.close()

    def create_or_update_token(self, session_token, refresh_token, expired_time, user_id):
        # th = threading.Thread(target=self.__create_or_update_token,
        #                       args=(session_token, refresh_token, expired_time, user_id))
        # th.daemon = True
        # th.start()
        # logger.info("is th alive" + str(th.is_alive()))
        self.__create_or_update_token(session_token, refresh_token, expired_time, user_id)
        # Delete old cache if have
        if cache.get(('Sessions_Manager', 'user_id', user_id)):
            old_session = cache.get(('Sessions_Manager', 'user_id', user_id))
            cache.delete(('Sessions_Manager', 'session_token', old_session['session_token']))
            cache.delete(('Sessions_Manager', 'refresh_token', old_session['refresh_token']))
            cache.delete(('Sessions_Manager', 'user_id', old_session['user_id']))
        # Add new cache
        new_session = {'user_id': user_id, 'session_token': session_token, 'refresh_token': refresh_token,
                       'expired_time': expired_time}
        cache.set(('Sessions_Manager', 'session_token', new_session['session_token']), new_session)
        cache.set(('Sessions_Manager', 'refresh_token', new_session['refresh_token']), new_session)
        cache.set(('Sessions_Manager', 'user_id', new_session['user_id']), new_session)

    def get_by_session_token(self, session_token):
        if cache.get(('Sessions_Manager', 'session_token', session_token)):
            return cache.get(('Sessions_Manager', 'session_token', session_token))

        query = self.filter(session_token=session_token)
        if not query.exists():
            return None
        else:
            return query.first().serialize()

    def get_by_refresh_token(self, refresh_token, user_id):
        if cache.get(('Sessions_Manager', 'refresh_token', refresh_token)):
            return cache.get(('Sessions_Manager', 'refresh_token', refresh_token))
        query = self.filter(refresh_token=refresh_token, user_id=user_id)
        if not query.exists():
            return None
        else:
            return query.first().serialize()

    def delete_session_token(self, session_token):
        if cache.get(('Sessions_Manager', 'session_token', session_token)):
            old_session = cache.get(('Sessions_Manager', 'session_token', session_token))
            cache.delete(('Sessions_Manager', 'session_token', old_session['session_token']))
            cache.delete(('Sessions_Manager', 'refresh_token', old_session['refresh_token']))
            cache.delete(('Sessions_Manager', 'user_id', old_session['user_id']))
        self.filter(session_token=session_token).delete()

    def cache_all_session(self):
        sessions = self.all()
        for session in sessions:
            session = session.serialize()
            cache.set(('Sessions_Manager', 'session_token', session['session_token']), session)
            cache.set(('Sessions_Manager', 'refresh_token', session['refresh_token']), session)
            cache.set(('Sessions_Manager', 'user_id', session['user_id']), session)


class SessionsModel(models.Model):
    session_token = models.CharField(max_length=255, null=False, unique=True)
    refresh_token = models.CharField(max_length=255, null=False, unique=True)
    expired_time = models.BigIntegerField(null=False)
    user = models.OneToOneField('UsersModel', on_delete=models.CASCADE)
    objects = SessionsManager()

    def __str__(self):
        return self.session_token + " " + str(self.expired_time)

    def serialize(self):
        return {'user_id': self.user.id, 'session_token': self.session_token, 'refresh_token': self.refresh_token,
                'expired_time': self.expired_time}

    class Meta:
        db_table = "sessions_tb"
