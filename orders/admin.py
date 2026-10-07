from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'crop',
        'retailer',
        'farmer',
        'ordered_qty',
        'total_price',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at', 'crop__unit')
    search_fields = (
        'retailer__username',
        'farmer__username',
        'crop__crop_name',
    )
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Parties', {
            'fields': ('retailer', 'farmer')
        }),
        ('Crop & Quantity', {
            'fields': ('crop', 'ordered_qty', 'total_price')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    @admin.action(description='Mark selected orders as Confirmed')
    def mark_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f"{updated} order(s) marked as Confirmed.")

    @admin.action(description='Mark selected orders as Completed')
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} order(s) marked as Completed.")

    @admin.action(description='Mark selected orders as Cancelled')
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} order(s) marked as Cancelled.")