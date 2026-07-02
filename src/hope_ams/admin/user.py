from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from hope_ams.models import AMSUser

from .base import BaseAdmin


@admin.register(AMSUser)
class AMSUserAdmin(BaseAdmin[AMSUser], DjangoUserAdmin[AMSUser]):
    pass
