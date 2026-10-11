from django.test import TestCase

# Create your tests here.
from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from marketplace.models import CropProduce
from .models import Order


class OrderModelTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.retailer = User.objects.create_user(username='retailer', password='pass12345')
        self.retailer.profile.role = 'retailer'
        self.retailer.profile.save()

        self.crop = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore',
        )

        self.order = Order.objects.create(
            retailer=self.retailer,
            farmer=self.farmer,
            crop=self.crop,
            ordered_qty=Decimal('10'),
            total_price=Decimal('850'),
            status='pending',
        )

    def test_order_str(self):
        self.assertIn('Wheat', str(self.order))
        self.assertIn('Pending', str(self.order))

    def test_reverse_relations(self):
        self.assertEqual(self.farmer.orders_received.count(), 1)
        self.assertEqual(self.retailer.orders_placed.count(), 1)
        self.assertEqual(self.crop.orders.count(), 1)

    def test_is_pending(self):
        self.assertTrue(self.order.is_pending)
        self.assertFalse(self.order.is_confirmed)

    def test_can_be_cancelled_pending(self):
        self.assertTrue(self.order.can_be_cancelled())

    def test_can_be_cancelled_confirmed(self):
        self.order.status = 'confirmed'
        self.order.save()
        self.assertTrue(self.order.can_be_cancelled())

    def test_cannot_be_cancelled_completed(self):
        self.order.status = 'completed'
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())

    def test_cannot_be_cancelled_cancelled(self):
        self.order.status = 'cancelled'
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())


class PlaceOrderViewTests(TestCase):
    """The most important tests: order placement + stock deduction."""

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.retailer = User.objects.create_user(username='retailer', password='pass12345')
        self.retailer.profile.role = 'retailer'
        self.retailer.profile.save()

        self.crop = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore', is_available=True,
        )

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse('place_order', args=[self.crop.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_farmer_blocked(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('place_order', args=[self.crop.pk]))
        self.assertRedirects(response, reverse('dashboard'))

    def test_place_order_reduces_stock(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '25',
            'notes': '',
        })
        self.crop.refresh_from_db()
        self.assertEqual(self.crop.quantity, Decimal('75.00'))
        self.assertEqual(Order.objects.count(), 1)

    def test_place_order_computes_total_correctly(self):
        self.client.login(username='retailer', password='pass12345')
        self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '10',
            'notes': 'Urgent',
        })
        order = Order.objects.first()
        self.assertEqual(order.total_price, Decimal('850.00'))
        self.assertEqual(order.notes, 'Urgent')
        self.assertEqual(order.status, 'pending')

    def test_over_order_is_rejected(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '150',
            'notes': '',
        })
        # No order created
        self.assertEqual(Order.objects.count(), 0)
        # Stock unchanged
        self.crop.refresh_from_db()
        self.assertEqual(self.crop.quantity, Decimal('100.00'))
        # Form re-rendered (200) with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only')

    def test_ordering_exact_stock_marks_crop_unavailable(self):
        self.client.login(username='retailer', password='pass12345')
        self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '100',
            'notes': '',
        })
        self.crop.refresh_from_db()
        self.assertEqual(self.crop.quantity, Decimal('0.00'))
        self.assertFalse(self.crop.is_available)

    def test_two_consecutive_orders_cannot_both_take_full_stock(self):
        """
        Simulates the oversell scenario sequentially.
        SQLite ignores select_for_update, so this test relies on the
        application-level re-check inside the transaction.

        On PostgreSQL, the row lock handles true concurrency.
        """
        retailer2 = User.objects.create_user(username='retailer2', password='pass12345')
        retailer2.profile.role = 'retailer'
        retailer2.profile.save()

        # Retailer 1 orders the full stock
        self.client.login(username='retailer', password='pass12345')
        self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '100',
            'notes': '',
        })

        # Retailer 2 tries to order the same 100
        self.client.logout()
        self.client.login(username='retailer2', password='pass12345')
        response = self.client.post(reverse('place_order', args=[self.crop.pk]), {
            'ordered_qty': '100',
            'notes': '',
        })

        self.crop.refresh_from_db()
        self.assertEqual(self.crop.quantity, Decimal('0.00'))
        # Only one order should exist
        self.assertEqual(Order.objects.count(), 1)
        # Second attempt gets an error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only')


class OrderManagementViewTests(TestCase):

    def setUp(self):
        self.farmer = User.objects.create_user(username='farmer', password='pass12345')
        self.farmer.profile.role = 'farmer'
        self.farmer.profile.save()

        self.retailer = User.objects.create_user(username='retailer', password='pass12345')
        self.retailer.profile.role = 'retailer'
        self.retailer.profile.save()

        self.other_retailer = User.objects.create_user(username='other', password='pass12345')
        self.other_retailer.profile.role = 'retailer'
        self.other_retailer.profile.save()

        self.crop = CropProduce.objects.create(
            farmer=self.farmer, crop_name='Wheat',
            quantity=Decimal('100'), unit='kg', price=Decimal('85'),
            harvest_date=date.today(), location='Lahore',
        )
        self.order = Order.objects.create(
            retailer=self.retailer, farmer=self.farmer, crop=self.crop,
            ordered_qty=Decimal('10'), total_price=Decimal('850'), status='pending',
        )

    def test_my_orders_retailer_only(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('my_orders'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_incoming_orders_farmer_only(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.get(reverse('incoming_orders'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_order_detail_cross_user_404(self):
        self.client.login(username='other', password='pass12345')
        response = self.client.get(reverse('order_detail', args=[self.order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_order_detail_accessible_by_retailer(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.get(reverse('order_detail', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)

    def test_order_detail_accessible_by_farmer(self):
        self.client.login(username='farmer', password='pass12345')
        response = self.client.get(reverse('order_detail', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)

    def test_farmer_confirms_order(self):
        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_confirm', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')

    def test_farmer_completes_confirmed_order(self):
        self.order.status = 'confirmed'
        self.order.save()
        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_complete', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_farmer_cannot_complete_pending_order(self):
        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_complete', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')  # unchanged

    def test_farmer_cannot_confirm_confirmed_order(self):
        self.order.status = 'confirmed'
        self.order.save()
        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_confirm', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')  # unchanged

    def test_cancel_restores_stock(self):
        # Simulate the original order: stock was reduced by 10, from 100 to 90
        self.crop.quantity = Decimal('90')
        self.crop.save()

        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_cancel', args=[self.order.pk]))

        self.order.refresh_from_db()
        self.crop.refresh_from_db()

        self.assertEqual(self.order.status, 'cancelled')
        self.assertEqual(self.crop.quantity, Decimal('100.00'))

    def test_cancel_restores_availability(self):
        self.crop.quantity = Decimal('0')
        self.crop.is_available = False
        self.crop.save()

        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_cancel', args=[self.order.pk]))

        self.crop.refresh_from_db()
        self.assertTrue(self.crop.is_available)
        self.assertEqual(self.crop.quantity, Decimal('10.00'))

    def test_cannot_cancel_completed_order(self):
        self.order.status = 'completed'
        self.order.save()
        self.client.login(username='farmer', password='pass12345')
        self.client.post(reverse('order_cancel', args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')  # unchanged

    def test_cannot_cancel_other_farmers_order(self):
        other_farmer = User.objects.create_user(username='otherfarmer', password='pass12345')
        other_farmer.profile.role = 'farmer'
        other_farmer.profile.save()
        self.client.login(username='otherfarmer', password='pass12345')
        response = self.client.post(reverse('order_cancel', args=[self.order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_retailer_cannot_cancel(self):
        self.client.login(username='retailer', password='pass12345')
        response = self.client.post(reverse('order_cancel', args=[self.order.pk]))
        # role_required redirects to dashboard
        self.assertEqual(response.status_code, 302)