from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class CropProduce(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilogram (Kg)'),
        ('maund', 'Maund (40 Kg)'),
    )

    farmer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='crops'
    )
    crop_name = models.CharField(max_length=100)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Available quantity in the selected unit."
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default='kg'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit in PKR."
    )
    harvest_date = models.DateField()
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Crop Produce'
        verbose_name_plural = 'Crop Produce'

    def __str__(self):
        return f"{self.crop_name} — {self.farmer.username}"

    def get_absolute_url(self):
        return reverse('crop_detail', args=[self.pk])

    @property
    def total_value(self):
        """Approximate total value of this listing at current price."""
        return self.quantity * self.price