from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('', ViewNews.as_view(), name='news'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)