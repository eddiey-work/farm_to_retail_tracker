from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from marketplace.models import CropProduce


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    retailer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders_placed"
    )
    farmer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders_received"
    )
    crop = models.ForeignKey(
        CropProduce, on_delete=models.PROTECT, related_name="orders"
    )
    ordered_qty = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.pk} — {self.crop.crop_name} ({self.get_status_display()})"

    @property
    def is_pending(self):
        return self.status == "pending"

    @property
    def is_confirmed(self):
        return self.status == "confirmed"

    @property
    def is_completed(self):
        return self.status == "completed"

    @property
    def is_cancelled(self):
        return self.status == "cancelled"

    def can_be_cancelled(self):
        """Only pending or confirmed orders can still be cancelled."""
        return self.status in ("pending", "confirmed")
