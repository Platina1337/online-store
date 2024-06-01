from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('dialogs/<int:member_from>/', DialogsView.as_view(), name='dialogs_view'),
    path('create_dialog/<int:id>/', create_dialog, name='create_dialog'),
    path('list_chats/', ListChatsView.as_view(), name='list_chats'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)