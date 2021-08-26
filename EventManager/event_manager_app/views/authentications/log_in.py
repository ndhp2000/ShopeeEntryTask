import json
import time

from django.utils.decorators import method_decorator

from ..base import BaseView
from ...authentications.hashing import HashingUtil
from ...models.users import UsersModel
from ...sessions.session import SessionInstance
from django.views.decorators.csrf import csrf_exempt

import logging

# Get an instance of a logger
logger = logging.getLogger('django')


@method_decorator(csrf_exempt, name='dispatch')
class LogInView(BaseView):

    def __init__(self):
        super(LogInView, self).__init__(log_in_required=False, admin_required=False)

    def deserialize_request(self, request, *args, **kwargs):
        logger.info("PARSING: " + json.dumps(request.POST))
        # Deserialize request data
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        # Check condition
        if username is None:
            self.serialize_error_response("Invalid username")
            return False
        if password is None:
            self.serialize_error_response("Invalid password")
            return False

        # Save request data
        self.request_data['username'] = username
        self.request_data['password'] = password
        return True

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        start_time = time.time()
        logger.info("RECEIVED POST: ")
        # Deserialize Request
        if not self.deserialize_request(request, *args, **kwargs):
            return self.response

        # process_time = time.time() - start_time
        # logger.info("PROCESS DESERIALIZE TIME " + str(process_time))
        # start_time = time.time()

        # DB Call
        logger.info("DB CALLED: ")
        user = UsersModel.objects.get_user_by_username(self.request_data['username'])

        # process_time = time.time() - start_time
        # logger.info("PROCESS CALL-DB TIME " + str(process_time))

        # Make response
        # User not exist
        if user is None:
            self.serialize_error_response("User not found")
            logger.info("USER NOT FOUND: ")
            return self.response
        # Check password
        password_authenticator = HashingUtil(self.request_data['password'])

        start_time = time.time()
        if password_authenticator.compare_hash(user['password']):

            # process_time = time.time() - start_time
            # logger.info("PROCESS HASH PASSWORD TIME " + str(process_time))
            # start_time = time.time()

            session_token, refresh_token = SessionInstance.create(user['id'], user['username'], user['password'])
            self.serialize_success_response("Log-in Successfully",
                                            data={'session_token': session_token, 'refresh_token': refresh_token,
                                                  'user_id': user['id'], 'username': user['username']}
                                            )
            self.response.set_cookie("_sessionToken", session_token, secure=True, samesite='strict')

            # process_time = time.time() - start_time
            # logger.info("PROCESS CREATE SESSION TIME " + str(process_time))

            logger.info("SUCCESS LOG IN: ")
        else:
            self.serialize_error_response("Incorrect password")
            logger.info("WRONG PASSWORD: ")

        return self.response
