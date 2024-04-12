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
    path('login/', user_login, name='login'),
    path('logout/', logout_user, name="logout"),
    path('csrf_failure/', csrf_failure, name='csrf_failure'),
    path('like/<int:material_id>/', like_material, name='like_material'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)