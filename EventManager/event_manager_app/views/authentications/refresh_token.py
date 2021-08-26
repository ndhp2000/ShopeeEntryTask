from ..base import BaseView
from ...authentications.hashing import HashingUtil
from ...models.users import UsersModel
from ...sessions.session import SessionInstance

import logging

# Get an instance of a logger
logger = logging.getLogger('django')


class RefreshToken(BaseView):

    def __init__(self):
        super(RefreshToken, self).__init__(log_in_required=False, admin_required=False)

    def deserialize_request(self, request, *args, **kwargs):
        # Deserialize request data
        refresh_token = request.POST.get('refresh_token', None)

        # Check condition
        if refresh_token is None:
            self.serialize_error_response("Invalid refresh_token")
            return False

        self.session_token = request.COOKIES.get('_sessionToken', None)
        if self.session_token is None:
            self.serialize_error_response("Invalid session_token")
            return False

        session = SessionInstance.get_instance(token=self.session_token)
        if session['refresh_token'] != refresh_token:
            self.serialize_error_response("Invalid refresh_token")
            return False

        # Save request data
        self.request_data['refresh_token'] = refresh_token
        self.request_data['user_id'] = session['user_id']
        return True

    def post(self, request, *args, **kwargs):
        logger.info("RECEIVED POST: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # DB Call
        user = UsersModel.objects.get_user_model_by_id(self.request_data['user_id'])

        # Make response
        # User not exist
        if user is None:
            self.serialize_error_response("User not found")
            return self.response
        # Check password
        user = user.serialize()

        session_token, refresh_token = SessionInstance.refresh(self.request_data['refresh_token'],
                                                               user['id'], user['username'], user['password'])
        if session_token is None or refresh_token is None:
            self.serialize_error_response("Error when refresh token, please log-in again")
            logger.info("ERROR REFRESH TOKEN: ")
            return self.response
        else:
            self.serialize_success_response("Refresh token Successfully",
                                            data={'session_token': session_token, 'refresh_token': refresh_token,
                                                  'user_id': user['id'], 'username': user['username']}
                                            )
            self.response.set_cookie("_sessionToken", session_token, secure=True,samesite='strict')
            logger.info("REFRESH TOKEN SUCCESS: ")
            return self.response
