from ..base import BaseView
from ...sessions.session import SessionInstance
import logging

# Get an instance of a logger
logger = logging.getLogger('django')


class LogOutView(BaseView):

    def __init__(self):
        super(LogOutView, self).__init__(log_in_required=True, admin_required=False)

    def post(self, request, *args, **kwargs):
        logger.info("RECEIVED POST: ")
        # Deserialize Request

        # DB Call
        SessionInstance.remove(self.session_token)

        # Make response
        self.serialize_success_response("Log-out Successfully")
        self.response.delete_cookie("_sessionToken",samesite='strict')

        return self.response
