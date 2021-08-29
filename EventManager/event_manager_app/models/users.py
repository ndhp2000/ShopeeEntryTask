import logging

from django.db import models
from django.core.cache import cache

# Get an instance of a logger
logger = logging.getLogger('django')


class UsersManager(models.Manager):

    def get_user_by_username(self, username):
        if cache.get(('USERS_MANAGER', username)):
            return cache.get(('USERS_MANAGER', username))

        # CACHE cho nay
        user = self.filter(username=username).first()
        if user is None:
            return None
        else:
            user = user.serialize()
            cache.set(('USERS_MANAGER', username), user)
            return user

    def cache_all_username(self):
        logger.warning("START LOAD USERS TO CACHE")
        users = self.all()[:10000]
        for user in users:
            cache.set(('USERS_MANAGER', user.username), user.serialize())
        logger.warning("DONE LOAD USERS TO CACHE")

    def get_user_model_by_id(self, user_id):
        user = self.filter(id=user_id)
        if not user.exists():
            return None
        else:
            return user.first()


class UsersModel(models.Model):
    username = models.CharField(max_length=64, unique=True, null=False, db_index=True)
    password = models.CharField(max_length=512, null=False)
    name = models.CharField(max_length=64, null=False)
    avatar_url = models.CharField(max_length=512, null=False, blank=True)
    is_admin = models.BooleanField(default=False, null=False)
    objects = UsersManager()

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users_tb"

    def serialize(self):
        return {'id': self.id, 'username': self.username, 'password': self.password, 'name': self.name,
                'avatar_url': self.avatar_url,
                'is_admin': self.is_admin}

    def short_serialize(self):
        return {'user_id': self.id, 'name': self.name, 'avatar_url': self.avatar_url}
