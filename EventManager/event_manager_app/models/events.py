import time

from django.conf import settings
from django.db import models, DatabaseError

from .comments import CommentsModel
from .users import UsersModel


class EventsManager(models.Manager):
    def get_events_list(self, page, category_id, begin_date, end_date):
        events_list_query = self.all()
        # Filter by category
        if category_id is not None:
            events_list_query = events_list_query.filter(category_id=category_id)

        # Filter by date
        if begin_date is not None:
            events_list_query = events_list_query.filter(date__gte=begin_date)
        if end_date is not None:
            events_list_query = events_list_query.filter(date__lte=end_date)

        # Count
        n_events = events_list_query.count()  # evaluate 1

        # Limit
        limit_records = settings.APP_CONFIG['ENTRY_LIMIT_PER_PAGE']
        offset = (page - 1) * limit_records

        # Check page arguments
        if offset > n_events:
            return None

        events_list_query = events_list_query.order_by('id')[offset: offset + limit_records].select_related()

        # Get List
        events_list = [q.serialize() for q in events_list_query]  # evaluate 2

        return {'event_list': events_list, 'n_events': n_events}

    def get_event_model_by_id(self, event_id):
        event = self.filter(id=event_id)
        if not event.exists():
            return None
        else:
            return event.first()

    def get_event_by_id(self, event_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None
        return event.serialize()

    def get_event_participants_by_id(self, event_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None

        participants = event.participants.all()
        n_participants = participants.count()
        participants_list = [q.short_serialize() for q in participants]
        return {'participants_list': participants_list, 'n_participants': n_participants}

    def add_participant_by_event_id(self, event_id, user_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"

        event.participants.add(user)
        return True, None

    def delete_participant_by_event_id(self, event_id, user_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"

        event.participants.remove(user)
        return True, None

    def get_event_likes_by_id(self, event_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None

        likes = event.likes.all()
        n_likes = likes.count()
        likes_list = [q.short_serialize() for q in likes]
        return {'likes_list': likes_list, 'n_likes': n_likes}

    def add_like_by_event_id(self, event_id, user_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"

        event.likes.add(user)
        return True, None

    def delete_like_by_event_id(self, event_id, user_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"

        event.likes.remove(user)
        return True, None

    def get_event_comments_by_id(self, event_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None

        query = CommentsModel.objects.filter(event_id=event_id).select_related()

        n_comments = query.count()
        comments_list = []
        for q in query:
            comment = q.serialize()
            user = q.user.short_serialize()
            comment.update(user)
            comments_list.append(comment)
        return {'comment_list': comments_list, 'n_comments': n_comments}

    def add_comment_by_event_id(self, event_id, user_id, comment_content):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"
        try:
            comment = CommentsModel.objects.create(comment_content=comment_content,
                                                   comment_time=int(time.time() * 1000000),
                                                   user=user, event=event)
        except DatabaseError as e:
            return None, "Invalid argument: comment_content"

        return {'new_user': user.short_serialize(), 'comment': comment.serialize()}, None

    def delete_comment_by_event_id(self, event_id, user_id, comment_id):
        event = self.get_event_model_by_id(event_id)
        if event is None:
            return None, "Invalid argument: event_id"

        user = UsersModel.objects.get_user_model_by_id(user_id)
        if user is None:
            return None, "Invalid argument: user_id"

        comments = CommentsModel.objects.filter(id=comment_id).filter(user_id=user_id).filter(
            event_id=event_id)
        if not comments.exists():
            return None, "Invalid argument: comment_id"

        for comment in comments:
            comment.delete()

        return True, None

    def add_event(self, event_data):
        event = self.create(title=event_data['title'], description=event_data['description'],
                            location=event_data['location'], date=event_data['date'], image_url=event_data['image_url'],
                            category_id=event_data['category_id'])
        return event.serialize()


class EventsModel(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.CharField(max_length=1024, null=False, blank=True)
    location = models.CharField(max_length=1024, null=False, blank=True)
    date = models.BigIntegerField(null=False, blank=True, db_index=True)
    image_url = models.CharField(max_length=512, null=False, blank=True)
    category = models.ForeignKey('CategoriesModel', on_delete=models.PROTECT)
    likes = models.ManyToManyField(UsersModel, related_name='like_relation')
    participants = models.ManyToManyField(UsersModel, related_name='participate_relation')
    objects = EventsManager()

    def __str__(self):
        return self.title

    class Meta:
        db_table = "events_tb"

    def serialize(self):
        return {'id': self.id, 'title': self.title, 'description': self.description, 'location': self.location,
                'date': self.date,
                'image_url': self.image_url, 'category_name': self.category.category_name}
