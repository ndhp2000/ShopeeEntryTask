import logging

from .event import EventView
from ...models.events import EventsModel

logger = logging.getLogger('django')


class EventLikesView(EventView):
    def __init__(self):
        super(EventLikesView, self).__init__()

    def get(self, request, *args, **kwargs):
        logger.info("RECEIVED GET: ")

        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        event_likes = EventsModel.objects.get_event_likes_by_id(self.request_data['event_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if event_likes is None:
            self.serialize_error_response("Invalid argument: event_id")
            return self.response

        self.serialize_success_response("Get Event Likes Success", data=event_likes)
        return self.response

    def post(self, request, *args, **kwargs):
        logger.info("RECEIVED POST: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.add_like_by_event_id(self.request_data['event_id'],
                                                                    self.request_data['user_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Add Event Like Success!")
        return self.response

    def delete(self, request, *args, **kwargs):
        logger.info("RECEIVED DELETE: ")

        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.delete_like_by_event_id(self.request_data['event_id'],
                                                                       self.request_data['user_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Delete Event Like Success!")
        return self.response
