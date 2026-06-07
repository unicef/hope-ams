from django.urls import path

from . import views

urlpatterns = [
    path("run/", views.submit_run, name="submit-run"),
    path("runs/<uuid:run_id>/", views.run_detail, name="run-detail"),
    path("anomalies/", views.anomaly_list, name="anomaly-list"),
    path("anomalies/<uuid:anomaly_id>/", views.anomaly_update, name="anomaly-update"),
    path("stats/", views.stats, name="stats"),
    path("rules/", views.rule_config_list, name="rule-config-list"),
]
