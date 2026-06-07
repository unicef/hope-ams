from django.contrib.admin import AdminSite


class AMSAdminSite(AdminSite):
    site_header = "Anomaly Management System"
    site_title = "AMS Admin"
    index_title = "AMS Dashboard"
