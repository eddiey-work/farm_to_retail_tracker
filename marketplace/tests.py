from django.test import TestCase

# Create your tests here.
from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import CropProduce
from .forms import CropForm, OrderForm
from orders.models import Order


class CropProduceModelTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

    def test_crop_str_contains_name_and_farmer(self):
        crop = CropProduce.objects.create(
            farmer=self.farmer,
            crop_name='Wheat',
            quantity=Decimal('100.00'),
            unit='kg',
            price=Decimal('85.00'),
            harvest_date=date.today(),
            location='Lahore',
        )
        self.assertIn('Wheat', str(crop))
        self.assertIn('farmer', str(crop))

    def test_total_value_property(self):
        crop = CropProduce.objects.create(
            farmer=self.farmer,
            crop_name='Wheat',
            quantity=Decimal('100.00'),
            unit='kg',
            price=Decimal('85.00'),
            harvest_date=date.today(),
            location='Lahore',
        )
        self.assertEqual(crop.total_value, Decimal('8500.00'))

    def test_get_absolute_url(self):
        crop = CropProduce.objects.create(
            farmer=self.farmer,
            crop_name='Rice',
            quantity=Decimal('50.00'),
            unit='kg',
            price=Decimal('250.00'),
            harvest_date=date.today(),
            location='Faisalabad',
        )
        self.assertEqual(crop.get_absolute_url(), reverse('crop_detail', args=[crop.pk]))

    def test_farmer_reverse_relation(self):
        CropProduce.objects.create(
            farmer=self.farmer, crop_name='A', quantity=Decimal('1'),
            unit='kg', price=Decimal('1'), harvest_date=date.today(), location='X'
        )
        CropProduce.objects.create(
            farmer=self.farmer, crop_name='B', quantity=Decimal('1'),
            unit='kg', price=Decimal('1'), harvest_date=date.today(), location='X'
        )
        self.assertEqual(self.farmer.crops.count(), 2)


class CropFormTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='f', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

    def test_valid_form_creates_crop(self):
        form = CropForm(data={
            'crop_name': 'Wheat',
            'quantity': '100',
            'unit': 'kg',
            'price': '85',
            'harvest_date': str(date.today()),
            'location': 'Lahore',
            'description': 'Fresh',
            'is_available': True,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_zero_quantity_fails(self):
        form = CropForm(data={
            'crop_name': 'Wheat',
            'quantity': '0',
            'unit': 'kg',
            'price': '85',
            'harvest_date': str(date.today()),
            'location': 'Lahore',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)


class MarketplaceViewTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.crop1 = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore', is_available=True,
        )
        self.crop2 = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Rice',
            quantity=Decimal('50'), unit='kg', price=Decimal('250'),
            harvest_date=date.today(), location='Faisalabad', is_available=True,
        )
        self.crop3 = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Sugarcane',
            quantity=Decimal('0'), unit='maund', price=Decimal('1800'),
            harvest_date=date.today(), location='Multan', is_available=False,
        )

    def test_marketplace_public(self):
        """Anonymous users can browse."""
        response = self.client.get(reverse('marketplace'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wheat')
        self.assertContains(response, 'Rice')

    def test_unavailable_crops_hidden(self):
        response = self.client.get(reverse('marketplace'))
        self.assertNotContains(response, 'Sugarcane')

    def test_search_filter(self):
        response = self.client.get(reverse('marketplace'), {'q': 'wheat'})
        self.assertContains(response, 'Wheat')
        self.assertNotContains(response, 'Rice')

    def test_location_filter(self):
        response = self.client.get(reverse('marketplace'), {'location': 'Lahore'})
        self.assertContains(response, 'Wheat')
        self.assertNotContains(response, 'Rice')

    def test_sort_by_price_low(self):
        response = self.client.get(reverse('marketplace'), {'sort': 'price_low'})
        crops = list(response.context['page_obj'])
        self.assertEqual(crops[0].crop_name, 'Wheat')  # 85 < 250
        self.assertEqual(crops[1].crop_name, 'Rice')

    def test_sort_by_price_high(self):
        response = self.client.get(reverse('marketplace'), {'sort': 'price_high'})
        crops = list(response.context['page_obj'])
        self.assertEqual(crops[0].crop_name, 'Rice')  # 250 > 85

    def test_crop_detail_loads(self):
        response = self.client.get(reverse('crop_detail', args=[self.crop1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wheat')
        self.assertContains(response, 'Lahore')

    def test_crop_detail_404_for_missing(self):
        response = self.client.get(reverse('crop_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class CropCRUDViewTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.other_farmer = User.objects.create_user(username='other', password='pass12345')
        self.other_farmer.profile.role = 'farmer'
        self.other_farmer.profile.save()

        self.retailer = User.objects.create_user(username='retailer', password='pass12345')
        self.retailer.profile.role = 'retailer'
        self.retailer.profile.save()

        self.my_crop = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore',
        )
        self.foreign_crop = CropProduce.objects.create(
            farmer=self.other_farmer, crop_name='Rice',
            quantity=Decimal('50'), unit='kg', price=Decimal('250'),
            harvest_date=date.today(), location='Faisalabad',
        )

    def test_my_crops_requires_login(self):
        response = self.client.get(reverse('my_crops'))
        self.assertEqual(response.status_code, 302)

    def test_my_crops_blocks_retailer(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.get(reverse('my_crops'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_my_crops_shows_only_own(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('my_crops'))
        self.assertContains(response, 'Wheat')
        self.assertNotContains(response, 'Rice')

    def test_crop_create_assigns_current_user_as_farmer(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.post(reverse('crop_create'), {
            'crop_name': 'Maize',
            'quantity': '200',
            'unit': 'kg',
            'price': '55',
            'harvest_date': str(date.today()),
            'location': 'Sahiwal',
            'description': '',
            'is_available': True,
        })
        self.assertRedirects(response, reverse('my_crops'))
        crop = CropProduce.objects.get(crop_name='Maize')
        self.assertEqual(crop.farmer, self.farmer)

    def test_crop_update_only_own(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('crop_update', args=[self.foreign_crop.pk]))
        self.assertEqual(response.status_code, 404)

    def test_crop_update_works_for_own(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.post(reverse('crop_update', args=[self.my_crop.pk]), {
            'crop_name': 'Wheat Premium',
            'quantity': '100',
            'unit': 'kg',
            'price': '95',
            'harvest_date': str(date.today()),
            'location': 'Lahore',
            'description': '',
            'is_available': True,
        })
        self.assertRedirects(response, reverse('my_crops'))
        self.my_crop.refresh_from_db()
        self.assertEqual(self.my_crop.crop_name, 'Wheat Premium')
        self.assertEqual(self.my_crop.price, Decimal('95.00'))

    def test_crop_delete_only_own(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('crop_delete', args=[self.foreign_crop.pk]))
        self.assertEqual(response.status_code, 404)

    def test_crop_delete_on_post_removes_crop(self):
        self.client.login(username='farmer', password='pass12345')
        pk = self.my_crop.pk
        response = self.client.post(reverse('crop_delete', args=[pk]))
        self.assertRedirects(response, reverse('my_crops'))
        self.assertFalse(CropProduce.objects.filter(pk=pk).exists())


class OrderFormTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='f', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()
        self.crop = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore', is_available=True,
        )

    def test_valid_quantity_accepted(self):
        form = OrderForm(data={'ordered_qty': '50', 'notes': ''}, crop=self.crop)
        self.assertTrue(form.is_valid(), form.errors)

    def test_quantity_exceeding_stock_fails(self):
        form = OrderForm(data={'ordered_qty': '150', 'notes': ''}, crop=self.crop)
        self.assertFalse(form.is_valid())
        self.assertIn('ordered_qty', form.errors)

    def test_zero_quantity_fails(self):
        form = OrderForm(data={'ordered_qty': '0', 'notes': ''}, crop=self.crop)
        self.assertFalse(form.is_valid())

    def test_unavailable_crop_fails(self):
        self.crop.is_available = False
        self.crop.save()
        form = OrderForm(data={'ordered_qty': '10', 'notes': ''}, crop=self.crop)
        self.assertFalse(form.is_valid())