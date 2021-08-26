import json
import logging
import random
import string
import time

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import DatabaseError
from django.utils.html import escape

from ..base import BaseView, to_int
from ...models.categories import CategoriesModel
from ...models.events import EventsModel

logger = logging.getLogger('django')


class EventsListView(BaseView):

    def __init__(self):
        super(EventsListView, self).__init__(log_in_required=True, admin_required=False)

    def deserialize_get_request(self, request, *args, **kwargs):

        # Deserialize request data
        request_page = request.GET.get('page', None)
        request_category_id = request.GET.get('category_id', None)
        request_begin_date = request.GET.get('begin_date', None)
        request_end_date = request.GET.get('end_date', None)

        # Check condition

        if request_page is None:
            request_page = 1
        else:
            request_page = to_int(request_page, None)
            if request_page is None or request_page <= 0:
                self.serialize_error_response("Invalid argument: page")
                return False

        if request_category_id is None:
            pass
        else:
            request_category_id = to_int(request_category_id, None)
            if request_category_id is None or not CategoriesModel.objects.is_category_existed(request_category_id):
                self.serialize_error_response("Invalid argument: category_id")
                return False

        if request_begin_date is None:
            pass
        else:
            request_begin_date = to_int(request_begin_date, None)
            if request_begin_date is None:
                self.serialize_error_response("Invalid argument: begin_date")
                return False

        if request_end_date is None:
            pass
        else:
            request_end_date = to_int(request_end_date, None)
            if request_end_date is None:
                self.serialize_error_response("Invalid argument: end_date")
                return False

        # Save request data
        self.request_data['page'] = request_page
        self.request_data['category_id'] = request_category_id
        self.request_data['begin_date'] = request_begin_date
        self.request_data['end_date'] = request_end_date
        logger.info("PARSING: " + json.dumps(self.request_data))
        return True

    def get(self, request, *args, **kwargs):
        logger.info("RECEIVED GET: ")
        # Deserialize Request
        if not self.deserialize_get_request(request, *args, **kwargs):
            return self.response

        # DB Call
        logger.info("DB CALLED: ")
        data = EventsModel.objects.get_events_list(self.request_data['page'], self.request_data['category_id'],
                                                   self.request_data['begin_date'], self.request_data['end_date'])

        # Make response
        if data is None:
            self.serialize_error_response("Invalid argument: page")
            logger.info("PROCESS ERROR PAGE: ")
            return self.response

        self.serialize_success_response("Get Event Lists Success", data=data)
        logger.info("PROCESS SUCCESS: ")
        return self.response

    def deserialize_post_request(self, request, *args, **kwargs):
        request_title = request.POST.get('title', None)
        if request_title is None:
            self.serialize_error_response("Not found argument: title")
            return False
        request_title = escape(request_title)

        request_description = escape(request.POST.get('description', ''))

        request_location = escape(request.POST.get('location', ''))

        request_date = request.POST.get('date', None)
        if request_date is None:
            request_date = 0
        else:
            request_date = to_int(request_date, None)
            if request_date is None:
                self.serialize_error_response("Invalid argument: date")
                return False

        request_category_id = request.POST.get('category_id', None)
        if request_category_id is None:
            self.serialize_error_response("Not found argument: category_id")
            return False
        else:
            request_category_id = to_int(request_category_id, None)
            if request_category_id is None or not CategoriesModel.objects.is_category_existed(request_category_id):
                self.serialize_error_response("Invalid argument: category_id")
                return False

        request_raw_image = request.FILES.get('raw_image', '')

        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        request_image_url = random_str + str(time.time()) + '.' + request_raw_image.name.split('.')[-1]
        print('request_image_url ', request_image_url)
        if request_raw_image == '':
            request_image_url = ''

        self.request_data['title'] = request_title
        self.request_data['description'] = request_description
        self.request_data['location'] = request_location
        self.request_data['date'] = request_date
        self.request_data['category_id'] = request_category_id
        self.request_data['image_url'] = request_image_url
        logger.info("PARSE DATA SUCCESS: " + json.dumps(self.request_data))
        self.request_data['raw_image'] = request_raw_image
        logger.info("PARSE RAW IMAGE SUCCESS :")
        return True

    def post(self, request, *args, **kwargs):

        logger.info("RECEIVED POST: ")
        # Must be admin - hard code
        if not self.is_admin(request):
            self.serialize_error_response("Log In as Administrator to use this feature")
            return self.response

        # Deserialize Request
        if not self.deserialize_post_request(request, *args, **kwargs):
            return self.response

        # Saved Image
        if self.request_data['raw_image'] != '':
            logger.info("Write image to: ", settings.STATIC_URL + 'img/' + self.request_data['image_url'])
            with default_storage.open(settings.STATIC_URL + 'img/' + self.request_data['image_url'],
                                      'wb+') as destination:
                for chunk in self.request_data['raw_image'].chunks():
                    destination.write(chunk)
            logger.info("SAVED IMAGE SUCCESS: ")

        # DB Call
        try:
            result = EventsModel.objects.add_event(self.request_data)
        except DatabaseError as e:
            logger.warning("ERROR WHEN INSERT NEW EVENT TO DB")
            self.serialize_error_response("Fail to add new Event to DB")
            return self.response
        
        logger.info("CALL DB SUCCESS: ")
        # Make response
        self.serialize_success_response("Successfully create event", {'new_event': result})
        logger.info("RETURN RESPONSE SUCCESS: ")
        return self.response
