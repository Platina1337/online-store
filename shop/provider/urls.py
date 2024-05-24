from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('', BuildingMaterialsCreateView.as_view(), name='main'),
    path('register/', RegistrationProviderView.as_view(), name='register'),
    path('login/', user_login, name='login'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)