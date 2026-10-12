from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('role', 'phone', 'location')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'username',
        'email',
        'get_role',
        'get_location',
        'crops_count',
        'orders_count',
        'is_staff',
    )
    list_filter = ('is_staff', 'is_active', 'profile__role')
    search_fields = ('username', 'email', 'profile__phone', 'profile__location')

    def get_role(self, obj):
        return obj.profile.get_role_display() if hasattr(obj, 'profile') else '—'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'profile__role'

    def get_location(self, obj):
        return obj.profile.location if hasattr(obj, 'profile') else '—'
    get_location.short_description = 'Location'

    def crops_count(self, obj):
        return obj.crops.count() if hasattr(obj, 'profile') and obj.profile.role == 'farmer' else '—'
    crops_count.short_description = 'Crops'

    def orders_count(self, obj):
        if not hasattr(obj, 'profile'):
            return '—'
        if obj.profile.role == 'farmer':
            return obj.orders_received.count()
        elif obj.profile.role == 'retailer':
            return obj.orders_placed.count()
        return '—'
    orders_count.short_description = 'Orders'


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'location', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone', 'location')
    readonly_fields = ('created_at', 'updated_at')