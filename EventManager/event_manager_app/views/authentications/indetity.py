import logging

import django

from ..base import BaseView

# Get an instance of a logger
logger = logging.getLogger('django')


class IdentityView(BaseView):

    def __init__(self):
        super(IdentityView, self).__init__(log_in_required=False, admin_required=False)

    def get(self, request, *args, **kwargs):
        logger.info("IDENTITY CSRF TOKEN REQUEST")
        token = django.middleware.csrf.get_token(request)
        self.serialize_success_response("Process Identity Successfully", {"csrf": token})
        return self.response
