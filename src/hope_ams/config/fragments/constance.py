CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

CONSTANCE_CONFIG = {
    "NEW_USER_IS_STAFF": (False, "Set new user as staff", bool),
    "NEW_USER_DEFAULT_GROUP": ("Default", "Group to assign to any new user", str),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "System Settings": (
        "NEW_USER_IS_STAFF",
        "NEW_USER_DEFAULT_GROUP",
    ),
}
