from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('home/', ViewHome.as_view(), name='home'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('', ViewIndex.as_view(), name='index'),
    path('register/', RegistrationView.as_view() , name='register'),
    path('login/', user_login , name='login'),
    path('login/', user_login , name='login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)