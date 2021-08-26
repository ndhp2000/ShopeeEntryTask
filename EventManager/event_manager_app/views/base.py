import logging

from django.http import JsonResponse
from django.views import View

from ..models import UsersModel
from ..sessions.session import SessionInstance
import traceback

logger = logging.getLogger('django')


def to_int(inp, default_value):
    if inp is None:
        return default_value
    try:
        return int(inp)
    except ValueError:
        return default_value


def to_str(inp, default_value):
    if inp is None:
        return default_value
    try:
        return str(inp)
    except ValueError:
        return default_value


class BaseView(View):
    STATUS_CODE = {'SUCCESS': 0, 'ERROR': 1, 'ERROR_TOKEN_EXPIRED': 2, 'ERROR_AUTHENTICATE': 3, 'EXCEPTION': -1}

    def __init__(self, log_in_required, admin_required):
        super(BaseView, self).__init__()
        self.log_in_required = log_in_required
        self.admin_required = admin_required
        self.response = JsonResponse(
            {'app_status_code': BaseView.STATUS_CODE['ERROR'], 'message': "ERROR: Server send the default response",
             'response_data': {}},
            status=200)
        self.request_data = {}
        self.session_token = ""

    def deserialize_request(self, request, *args, **kwargs):
        pass

    def __serialize_response__(self, html_status_code, app_status_code, data, message):
        self.response = JsonResponse(
            {'app_status_code': app_status_code, 'message': message, 'response_data': data},
            status=html_status_code)

    def serialize_success_response(self, message, data=None):
        if data is None:
            data = {}
        self.__serialize_response__(200, BaseView.STATUS_CODE['SUCCESS'], data, message)

    def serialize_error_response(self, message, data=None, app_status_code=None):
        if data is None:
            data = {}
        if app_status_code is None:
            app_status_code = BaseView.STATUS_CODE['ERROR']
        self.__serialize_response__(200, app_status_code, data, message)

    def serialize_exception_response(self, message=None, data=None):
        if data is None:
            data = {}
        if message is None:
            message = "Unknown exception was caught on server."
        self.__serialize_response__(500, BaseView.STATUS_CODE['EXCEPTION'], data,
                                    message)

    def dispatch(self, request, *args, **kwargs):
        try:
            if self.log_in_required:
                is_log_in = self.is_log_in(request)
                if is_log_in == -1:
                    self.serialize_error_response("Log In to use this feature", None,
                                                  BaseView.STATUS_CODE['ERROR_AUTHENTICATE'])
                    return self.response
                elif is_log_in == 0:
                    self.serialize_error_response("Session expired.", None, BaseView.STATUS_CODE['ERROR_TOKEN_EXPIRED'])
                    return self.response

            if self.admin_required and not self.is_admin(request):
                self.serialize_error_response("Log In as Administrator to use this feature")
                return self.response

            return super().dispatch(request, *args, **kwargs)

        except Exception as err:
            logger.warning("UNHANDLED EXCEPTION")
            logger.warning(traceback.format_exc())
            self.serialize_exception_response("UNHANDLE EXCEPTION")
            return self.response

    def is_log_in(self, request):
        self.session_token = request.COOKIES.get('_sessionToken', None)
        if self.session_token is None:
            return -1
        is_avail = SessionInstance.is_instance_available(self.session_token)
        if is_avail == 1:
            self.request_data['user_id'] = SessionInstance.get_instance(self.session_token)['user_id']
        return is_avail

    def is_admin(self, request):
        user = UsersModel.objects.get_user_model_by_id(self.request_data['user_id'])
        if user.is_admin:
            return True
        return False
