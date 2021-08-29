import logging
import threading
from queue import Queue
from time import sleep

from django.core.cache import cache
from django.db import models

# Get an instance of a logger
logger = logging.getLogger('django')


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue(0)
        self.status = 0

    # define your own run method
    def run(self):
        while True:
            while not self.queue.empty():
                session = self.queue.get()
                SessionsModel.objects.update_or_create(user_id=session['user_id'],
                                                       defaults={'session_token': session['session_token'],
                                                                 'refresh_token': session['refresh_token'],
                                                                 'expired_time': session['expired_time']})
            sleep(3)

    def add(self, session):
        self.queue.put(session)


WorkerInstance = Worker()


class SessionsManager(models.Manager):

    @staticmethod
    def is_session_token_existed(session_token):
        if cache.get(('Sessions_Manager', 'session_token', session_token)):
            return True
        return False

    @staticmethod
    def is_refresh_token_existed(refresh_token):
        if cache.get(('Sessions_Manager', 'refresh_token', refresh_token)):
            return True
        return False

    @staticmethod
    def __create_or_update_token(session_token, refresh_token, expired_time, user_id):
        if WorkerInstance.status == 0:
            WorkerInstance.start()
            WorkerInstance.status = 1

        WorkerInstance.add({
            'session_token': session_token, 'refresh_token': refresh_token,
            'expired_time': expired_time, 'user_id': user_id
        })
        # self.update_or_create(user_id=user_id,
        #                       defaults={'session_token': session_token,
        #                                 'refresh_token': refresh_token,
        #                                 'expired_time': expired_time})

    def create_or_update_token(self, session_token, refresh_token, expired_time, user_id):

        self.__create_or_update_token(session_token, refresh_token, expired_time, user_id)
        # Delete old cache if have

        old_session = cache.get(('Sessions_Manager', 'user_id', user_id))
        if old_session:
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
        sessions = self.all().select_related()[:10000]
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
