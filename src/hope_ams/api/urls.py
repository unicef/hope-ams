from django.urls import path

from . import views

urlpatterns = [
    path("check/", views.submit_check, name="check"),
    path("run/", views.submit_run, name="submit-run"),
    path("runs/<int:run_id>/", views.run_detail, name="run-detail"),
    path("anomalies/", views.anomaly_list, name="anomaly-list"),
    path("anomalies/<int:anomaly_id>/", views.anomaly_update, name="anomaly-update"),
    path("stats/", views.stats, name="stats"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
