from django import forms
from .models import CropProduce

from django.core.exceptions import ValidationError
from decimal import Decimal
from orders.models import Order

class OrderForm(forms.Form):
    ordered_qty = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Enter quantity',
        }),
        label='Quantity to order',
        help_text='Must not exceed the available quantity.',
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Any special instructions? (optional)',
        }),
        label='Notes',
    )

    def __init__(self, *args, crop=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.crop = crop

        if crop is not None:
            unit_label = crop.get_unit_display()
            self.fields['ordered_qty'].label = f'Quantity to order ({unit_label})'
            self.fields['ordered_qty'].help_text = (
                f'Available: {crop.quantity} {unit_label}. '
                f'Price: Rs. {crop.price} per {unit_label}.'
            )
            self.fields['ordered_qty'].widget.attrs['max'] = str(crop.quantity)

        # Apply Bootstrap styling
        for name, field in self.fields.items():
            css = 'form-control'
            field.widget.attrs['class'] = css

    def clean_ordered_qty(self):
        qty = self.cleaned_data['ordered_qty']
        if self.crop is None:
            return qty

        if qty > self.crop.quantity:
            raise ValidationError(
                f'Only {self.crop.quantity} {self.crop.get_unit_display()} available.'
            )
        if qty <= 0:
            raise ValidationError('Quantity must be greater than zero.')
        if not self.crop.is_available:
            raise ValidationError('This crop is currently unavailable.')
        return qty


class CropForm(forms.ModelForm):
    class Meta:
        model = CropProduce
        fields = (
            'crop_name',
            'quantity',
            'unit',
            'price',
            'harvest_date',
            'location',
            'description',
            'image',
            'is_available',
        )
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'crop_name': 'Crop name',
            'quantity': 'Quantity',
            'unit': 'Unit',
            'price': 'Price per unit (PKR)',
            'harvest_date': 'Harvest date',
            'location': 'Location / Mandi',
            'description': 'Description (optional)',
            'image': 'Crop photo (optional)',
            'is_available': 'Mark as available for sale',
        }
        help_texts = {
            'quantity': 'How much do you have to sell?',
            'price': 'Price per Kg or per Maund, in PKR.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = 'form-select' if field.widget.__class__.__name__ == 'Select' else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing} {css}".strip()

        # Checkbox shouldn't have form-control (it looks broken)
        if 'is_available' in self.fields:
            self.fields['is_available'].widget.attrs['class'] = 'form-check-input'

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Image must be smaller than 2 MB.")
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                raise forms.ValidationError("Only JPG, PNG, or WebP images are allowed.")
        return image