from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "email", "first_name", "last_name", "role", "is_active", "date_joined")
    list_display_links = ("pk", "username", "email")
    list_filter = ("role", "is_active", "date_joined")
    search_fields = ("username", "email")


admin.site.register(User, UserAdmin)
