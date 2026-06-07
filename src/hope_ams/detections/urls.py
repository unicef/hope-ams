from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("anomalies/", views.anomaly_list_view, name="anomaly-list-view"),
]
