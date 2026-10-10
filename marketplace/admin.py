from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CropProduce


@admin.register(CropProduce)
class CropProduceAdmin(admin.ModelAdmin):
    list_display = (
        "crop_name",
        "farmer",
        "quantity",
        "unit",
        "price",
        "location",
        "harvest_date",
        "is_available",
        "created_at",
    )
    list_filter = ("is_available", "unit", "location", "harvest_date")
    search_fields = ("crop_name", "farmer__username", "location", "description")
    list_editable = ("is_available",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Farmer", {"fields": ("farmer",)}),
        (
            "Crop Details",
            {"fields": ("crop_name", "quantity", "unit", "price", "harvest_date")},
        ),
        ("Location & Description", {"fields": ("location", "description", "image")}),
        ("Status", {"fields": ("is_available",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
