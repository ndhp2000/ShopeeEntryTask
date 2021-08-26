import logging

from .event import EventView
from ...models.events import EventsModel

logger = logging.getLogger('django')


class EventParticipantsView(EventView):
    def __init__(self):
        super(EventParticipantsView, self).__init__()

    def get(self, request, *args, **kwargs):
        logger.info("RECEIVED GET: ")

        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        event_participants = EventsModel.objects.get_event_participants_by_id(self.request_data['event_id'])

        # Make response
        if event_participants is None:
            self.serialize_error_response("Invalid argument: event_id")
            return self.response

        self.serialize_success_response("Get Event Participants Success", data=event_participants)
        return self.response

    def post(self, request, *args, **kwargs):
        logger.info("RECEIVED POST: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.add_participant_by_event_id(self.request_data['event_id'],
                                                                           self.request_data['user_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Add Event Participant Success!")
        return self.response

    def delete(self, request, *args, **kwargs):
        logger.info("RECEIVED DELETE: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        result, _message = EventsModel.objects.delete_participant_by_event_id(self.request_data['event_id'],
                                                                              self.request_data['user_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if result is None:
            self.serialize_error_response(_message)
        else:
            self.serialize_success_response("Delete Event Participant Success!")
        return self.response
