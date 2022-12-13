from urllib.parse import urlparse
from django.urls import path
from authentication import views


urlpatterns = [
    path('',views.log_user, name="login"),
    path('logout',views.log_out, name="logout")
]