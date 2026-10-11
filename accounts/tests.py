from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import UserProfile
from .forms import RegistrationForm


class UserProfileModelTests(TestCase):

    def test_profile_auto_created_on_user_creation(self):
        """Signal creates a UserProfile when a User is created."""
        user = User.objects.create_user(username='alice', password='pass12345')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)

    def test_default_role_is_farmer(self):
        user = User.objects.create_user(username='bob', password='pass12345')
        self.assertEqual(user.profile.role, 'farmer')

    def test_profile_str_contains_username_and_role(self):
        user = User.objects.create_user(username='carol', password='pass12345')
        user.profile.role = 'retailer'
        user.profile.save()
        self.assertIn('carol', str(user.profile))
        self.assertIn('Retailer', str(user.profile))

    def test_is_farmer_and_is_retailer_helpers(self):
        user = User.objects.create_user(username='dan', password='pass12345')
        user.profile.role = 'farmer'
        user.profile.save()
        self.assertTrue(user.profile.is_farmer())
        self.assertFalse(user.profile.is_retailer())

        user.profile.role = 'retailer'
        user.profile.save()
        self.assertFalse(user.profile.is_farmer())
        self.assertTrue(user.profile.is_retailer())


class RegistrationFormTests(TestCase):

    def test_valid_registration_creates_user_and_profile(self):
        form_data = {
            'username': 'newfarmer',
            'email': 'farmer@example.com',
            'password1': 'Str0ngPass!23',
            'password2': 'Str0ngPass!23',
            'role': 'farmer',
            'phone': '03001234567',
            'location': 'Lahore',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.username, 'newfarmer')
        self.assertEqual(user.email, 'farmer@example.com')
        self.assertEqual(user.profile.role, 'farmer')
        self.assertEqual(user.profile.phone, '03001234567')
        self.assertEqual(user.profile.location, 'Lahore')

    def test_password_mismatch_fails_validation(self):
        form_data = {
            'username': 'x',
            'email': 'x@example.com',
            'password1': 'Str0ngPass!23',
            'password2': 'DifferentPass!23',
            'role': 'farmer',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_role_fails_validation(self):
        form_data = {
            'username': 'y',
            'email': 'y@example.com',
            'password1': 'Str0ngPass!23',
            'password2': 'Str0ngPass!23',
            'role': 'admin',  # not a valid choice
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)


class AuthViewTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(
            username='farmer1', password='StrongPass!23'
        )
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.retailer = User.objects.create_user(
            username='retailer1', password='StrongPass!23'
        )
        self.retailer.profile.role = 'retailer'
        self.retailer.profile.save()

    def test_farmer_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'farmer1',
            'password': 'StrongPass!23',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_retailer_login_redirects_to_dashboard(self):
        response = self.client.post(reverse('login'), {
            'username': 'retailer1',
            'password': 'StrongPass!23',
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_wrong_password_does_not_log_in(self):
        response = self.client.post(reverse('login'), {
            'username': 'farmer1',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)  # re-rendered login page
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_farmer_dashboard_uses_farmer_template(self):
        self.client.login(username='farmer1', password='StrongPass!23')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'accounts/dashboard_farmer.html')

    def test_retailer_dashboard_uses_retailer_template(self):
        self.client.login(username='retailer1', password='StrongPass!23')
        response = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(response, 'accounts/dashboard_retailer.html')