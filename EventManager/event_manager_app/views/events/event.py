import json
import logging

from ..base import BaseView, to_int
from ...models.events import EventsModel

logger = logging.getLogger('django')


class EventView(BaseView):
    def __init__(self):
        super(EventView, self).__init__(log_in_required=True, admin_required=False)

    def deserialize_request(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        if event_id is None:
            self.serialize_error_response("Invalid argument: event_id")
            return False
        else:
            request_category_id = to_int(event_id, None)
            if request_category_id is None:
                self.serialize_error_response("Invalid argument: event_id")
                return False
        self.request_data['event_id'] = event_id
        logger.info("PARSING: " + json.dumps(self.request_data))
        return True

    def get(self, request, *args, **kwargs):
        logger.info("RECEIVED GET: ")

        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        event = EventsModel.objects.get_event_by_id(self.request_data['event_id'])
        logger.info("CALL DB SUCCESS: ")

        # Make response
        if event is None:
            self.serialize_error_response("Invalid argument: event_id")
            return self.response

        self.serialize_success_response("Get Event Success", data={'event': event})
        logger.info("RESPONSE SUCCESS: ")
        return self.response

