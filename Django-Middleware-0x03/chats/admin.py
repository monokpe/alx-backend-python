from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "last_name", "is_staff", "user_id")

    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "role",
                    "phone_number",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "role",
                    "phone_number",
                )
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
