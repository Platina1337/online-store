from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', BuildingMaterialsCreateView.as_view(), name='main'),
    path('messages/', BuildingMaterialsCreateView.as_view(), name='messages'),
    path('delete_material/', delete_material, name='delete_material'),
    path('list_posts/', ListPosts.as_view(), name='list_posts'),
    path('post_detail/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('add_post/', BuildingMaterialsCreateView.as_view(), name='add'),
    path('register/', RegistrationProviderView.as_view(), name='register'),
    path('login/', user_login, name='login'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)