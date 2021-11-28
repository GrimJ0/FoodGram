from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "email", "first_name", "last_name", "role", "is_active", "date_joined")
    search_fields = ("username",)


admin.site.register(User, UserAdmin)
