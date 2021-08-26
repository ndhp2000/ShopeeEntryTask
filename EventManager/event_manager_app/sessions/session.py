import base64
import hashlib
import random
import time

from django.conf import settings

from ..models import SessionsModel


class SessionDataStructure:

    @staticmethod
    def create_or_update(session_token, refresh_token, expired_time, user_id):
        if SessionsModel.objects.is_session_token_existed(session_token) \
                or SessionsModel.objects.is_refresh_token_existed(refresh_token):
            return False
        else:
            SessionsModel.objects.create_or_update_token(session_token, refresh_token, expired_time, user_id)
            return True

    @staticmethod
    def get(session_token):
        return SessionsModel.objects.get_by_session_token(session_token)

    @staticmethod
    def get_by_refresh_token(refresh_token, user_id):
        return SessionsModel.objects.get_by_refresh_token(refresh_token, user_id)

    @staticmethod
    def remove_session_token(session_token):
        SessionsModel.objects.delete_session_token(session_token)


class SessionManager:
    def __init__(self, time_limit):
        self.time_limit = time_limit
        self.sessionData = SessionDataStructure()

    @staticmethod
    def generate_token(user_id, username, password, time_generated):
        """
        SHA to create token
        """
        raw_token = username + str(user_id) + str(password) + str(time_generated)
        token = hashlib.sha256(raw_token.encode()).hexdigest()
        return token

    def create(self, user_id, username, password):
        """
        Create new token and add it to the token data.
        :param username:
        :param password:
        :param user_id:
        :return: token created to send to client
        """
        while True:
            # generate tokens
            token = self.generate_token(user_id, username, password, random.random())
            refresh_token = self.generate_token(user_id, username, password, random.random())
            expired_time = time.time() + self.time_limit
            # save to the data structure
            if self.sessionData.create_or_update(token, refresh_token, expired_time, user_id):
                return token, refresh_token

    def refresh(self, refresh_token, user_id, username, password):
        session_info = self.sessionData.get_by_refresh_token(refresh_token, user_id)
        if session_info is None:
            return None, None
        return self.create(user_id, username, password)

    def is_instance_available(self, token):

        session_info = self.sessionData.get(token)

        if session_info is None:
            return -1

        if time.time() > session_info['expired_time']:
            return 0

        return 1

    def get_instance(self, token):
        if self.is_instance_available(token) < 0:
            return None
        return self.sessionData.get(token)

    def remove(self, token):
        self.sessionData.remove_session_token(token)


SessionInstance = SessionManager(settings.APP_CONFIG['EXPIRE_TOKEN_PERIOD'])
