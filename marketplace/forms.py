from django import forms
from .models import CropProduce


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