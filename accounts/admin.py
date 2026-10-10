from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "location", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "phone", "location")
    readonly_fields = ("created_at", "updated_at")
