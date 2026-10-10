from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = (
        ("farmer", "Farmer"),
        ("retailer", "Retailer"),
    )

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)
    phone = forms.CharField(max_length=15, required=False)
    location = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # The signal already created a profile.
            # Now update it with the extra fields.
            profile = user.profile
            profile.role = self.cleaned_data["role"]
            profile.phone = self.cleaned_data["phone"]
            profile.location = self.cleaned_data["location"]
            profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = (
                "form-select"
                if field.widget.__class__.__name__ == "Select"
                else "form-control"
            )
            field.widget.attrs.update({"class": css})
