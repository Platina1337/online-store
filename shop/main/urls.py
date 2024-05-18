from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [

    path('home/', ViewHome.as_view(), name='home'),
    path('post/<int:id>/<slug:slug>/', product_detail, name='post-detail'),
    path('import_contacts_and_send_email/', import_contacts_and_send_email, name='import_contacts_and_send_email'),
    path('', ViewIndex.as_view(), name='index'),
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', user_login, name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', logout_user, name="logout"),
    path('csrf_failure/', csrf_failure, name='csrf_failure'),
    path('like/<int:material_id>/', like_material, name='like_material'),
    path('catalog/', ViewCatalog.as_view(), name='сatalog'),  # Путь для отображения каталога
    path('catalog/<str:url>/', filter_posts, name='filter_posts'),# Путь для фильтрации постов по категории
    path('search/', search_results, name='search_results'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)