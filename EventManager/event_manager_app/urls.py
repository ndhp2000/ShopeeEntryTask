from django.urls import path

from .views.authentications.indetity import IdentityView
from .views.authentications.log_in import LogInView
from .views.authentications.log_out import LogOutView
from .views.authentications.refresh_token import RefreshToken
from .views.events.event import EventView
from .views.events.event_comments import EventCommentsView
from .views.events.event_likes import EventLikesView
from .views.events.event_participants import EventParticipantsView
from .views.events.events_list import EventsListView

urlpatterns = [
    path(r'auth/login', LogInView.as_view(), name='auth_login'),  # POST
    path(r'auth/logout', LogOutView.as_view(), name='auth_logout'),  # POST
    path(r'auth/refresh_token', RefreshToken.as_view(), name='auth_refresh_token'),  # POST
    path(r'events', EventsListView.as_view(), name='events_list'),  # GET - POST
    path(r'events/<int:event_id>', EventView.as_view(), name='event'),  # GET
    path(r'events/<int:event_id>/participants', EventParticipantsView.as_view(),
         name='participants_list_of_event'),  # GET, POST, DEL
    path(r'events/<int:event_id>/likes', EventLikesView.as_view(), name='likes_list_of_event'),  # GET, POST, DEL
    path(r'events/<int:event_id>/comments', EventCommentsView.as_view(),
         name='comments_list_of_event'),  # GET, POST, DEL
    path(r'auth/identity', IdentityView.as_view(), name='identity')  # GET
]
