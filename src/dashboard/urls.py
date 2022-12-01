from urllib.parse import urlparse
from django.urls import path
from dashboard import views


urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('import', views.importCsv, name="importcsv")
]