from urllib.parse import urlparse
from django.urls import path
from dashboard import views
from dashboard.dash_apps import app1

# app_name = "dashboard"

urlpatterns = [
    path('', views.home, name="home"),
    path('import', views.importCsv, name="importcsv"),
    path('save', views.saveCsv, name="savecsv")

]