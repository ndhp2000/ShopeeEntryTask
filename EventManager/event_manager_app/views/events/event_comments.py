import json
import logging

from .event import EventView
from ..base import to_int
from ...models.events import EventsModel

logger = logging.getLogger('django')

from django.utils.html import escape


class EventCommentsView(EventView):
    def __init__(self):
        super(EventCommentsView, self).__init__()

    def deserialize_post_request(self, request, *args, **kwargs):
        comment_content = request.POST.get('comment_content', None)
        if comment_content is None:
            self.serialize_error_response("Not found argument: comment_content")
            return False

        self.request_data['comment_content'] = escape(comment_content)

        logger.info("PARSING: " + json.dumps(self.request_data))

        return True

    def deserialize_delete_request(self, request, *arg, **kwargs):
        comment_id = request.GET.get('comment_id', None)
        if comment_id is None:
            self.serialize_error_response("Not found argument: comment_id")
            return False
        else:
            comment_id = to_int(comment_id, None)
            if comment_id is None:
                self.serialize_error_response("Invalid argument: comment_id")
                return False
        self.request_data['comment_id'] = comment_id
        logger.info("PARSING: " + json.dumps(self.request_data))
        return True

    def get(self, request, *args, **kwargs):
        logger.info("RECEIVED GET: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        event_comments = EventsModel.objects.get_event_comments_by_id(self.request_data['event_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if event_comments is None:
            self.serialize_error_response("Invalid argument: event_id")
            return self.response

        self.serialize_success_response("Get Event Comments Success", data=event_comments)
        return self.response

    def post(self, request, *args, **kwargs):
        logger.info("RECEIVED POST: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        if not self.deserialize_post_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.add_comment_by_event_id(self.request_data['event_id'],
                                                                       self.request_data['user_id'],
                                                                       self.request_data['comment_content'])
        logger.info("CALL DB SUCCESS: ")
        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Add Event Comment Success!", data=result)
        return self.response

    def delete(self, request, *args, **kwargs):
        logger.info("RECEIVED DELETE: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        if not self.deserialize_delete_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.delete_comment_by_event_id(self.request_data['event_id'],
                                                                          self.request_data['user_id'],
                                                                          self.request_data['comment_id'])
        logger.info("CALL DB SUCCESS: ")
        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Delete Event Comment Success!")
        return self.response
