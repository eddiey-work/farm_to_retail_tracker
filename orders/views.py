from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required
from marketplace.models import CropProduce
from .models import Order


# ---------------------------------------------------------------------------
# LISTS
# ---------------------------------------------------------------------------

@role_required('retailer')
def my_orders(request):
    """All orders placed by the current retailer."""
    status_filter = request.GET.get('status', '').strip()

    orders = (
        Order.objects
        .filter(retailer=request.user)
        .select_related('crop', 'farmer')
        .order_by('-created_at')
    )

    if status_filter in ('pending', 'confirmed', 'completed', 'cancelled'):
        orders = orders.filter(status=status_filter)

    # Counts for the filter pills
    base = Order.objects.filter(retailer=request.user)
    counts = {
        'all': base.count(),
        'pending': base.filter(status='pending').count(),
        'confirmed': base.filter(status='confirmed').count(),
        'completed': base.filter(status='completed').count(),
        'cancelled': base.filter(status='cancelled').count(),
    }

    return render(request, 'orders/my_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'counts': counts,
    })


@role_required('farmer')
def incoming_orders(request):
    """All orders received on the current farmer's crops."""
    status_filter = request.GET.get('status', '').strip()

    orders = (
        Order.objects
        .filter(farmer=request.user)
        .select_related('crop', 'retailer')
        .order_by('-created_at')
    )

    if status_filter in ('pending', 'confirmed', 'completed', 'cancelled'):
        orders = orders.filter(status=status_filter)

    base = Order.objects.filter(farmer=request.user)
    counts = {
        'all': base.count(),
        'pending': base.filter(status='pending').count(),
        'confirmed': base.filter(status='confirmed').count(),
        'completed': base.filter(status='completed').count(),
        'cancelled': base.filter(status='cancelled').count(),
    }

    return render(request, 'orders/incoming_orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'counts': counts,
    })


# ---------------------------------------------------------------------------
# DETAIL
# ---------------------------------------------------------------------------

@login_required
def order_detail(request, pk):
    """Order detail. Visible only to the retailer or the farmer involved."""
    order = get_object_or_404(
        Order.objects.select_related('crop', 'farmer', 'retailer'),
        pk=pk
    )

    is_retailer = order.retailer == request.user
    is_farmer = order.farmer == request.user

    if not (is_retailer or is_farmer):
        raise Http404("Order not found.")

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'is_retailer': is_retailer,
        'is_farmer': is_farmer,
    })


# ---------------------------------------------------------------------------
# STATUS TRANSITIONS (FARMER ONLY)
# ---------------------------------------------------------------------------

@role_required('farmer')
def order_confirm(request, pk):
    """Farmer moves a pending order to confirmed."""
    order = get_object_or_404(Order, pk=pk, farmer=request.user)

    if request.method != 'POST':
        return redirect('order_detail', pk=order.pk)

    if order.status != 'pending':
        messages.error(request, f"Cannot confirm an order that is '{order.get_status_display()}'.")
        return redirect('order_detail', pk=order.pk)

    order.status = 'confirmed'
    order.save(update_fields=['status', 'updated_at'])
    messages.success(request, f"Order #{order.pk} has been confirmed.")
    return redirect('order_detail', pk=order.pk)


@role_required('farmer')
def order_complete(request, pk):
    """Farmer marks a confirmed order as completed."""
    order = get_object_or_404(Order, pk=pk, farmer=request.user)

    if request.method != 'POST':
        return redirect('order_detail', pk=order.pk)

    if order.status != 'confirmed':
        messages.error(request, f"Only confirmed orders can be marked completed. This one is '{order.get_status_display()}'.")
        return redirect('order_detail', pk=order.pk)

    order.status = 'completed'
    order.save(update_fields=['status', 'updated_at'])
    messages.success(request, f"Order #{order.pk} marked as completed.")
    return redirect('order_detail', pk=order.pk)


@role_required('farmer')
def order_cancel(request, pk):
    """
    Farmer cancels a pending or confirmed order.
    Stock is restored atomically.
    """
    order = get_object_or_404(Order, pk=pk, farmer=request.user)

    if request.method != 'POST':
        return redirect('order_detail', pk=order.pk)

    if not order.can_be_cancelled():
        messages.error(
            request,
            f"Orders that are '{order.get_status_display()}' cannot be cancelled."
        )
        return redirect('order_detail', pk=order.pk)

    try:
        with transaction.atomic():
            # Lock the order row
            locked_order = (
                Order.objects
                .select_for_update()
                .get(pk=order.pk)
            )

            # Re-check under lock
            if not locked_order.can_be_cancelled():
                raise ValidationError(
                    f"Order is now '{locked_order.get_status_display()}' and cannot be cancelled."
                )

            # Lock the crop row and restore stock
            crop = (
                CropProduce.objects
                .select_for_update()
                .get(pk=locked_order.crop.pk)
            )
            crop.quantity = (crop.quantity + locked_order.ordered_qty).quantize(Decimal('0.01'))
            crop.is_available = True
            crop.save()

            # Update the order
            locked_order.status = 'cancelled'
            locked_order.save(update_fields=['status', 'updated_at'])

        messages.success(
            request,
            f"Order #{order.pk} cancelled. "
            f"{order.ordered_qty} {order.crop.get_unit_display()} restored to your inventory."
        )
        return redirect('order_detail', pk=order.pk)

    except ValidationError as e:
        messages.error(request, e.messages[0] if e.messages else str(e))
        return redirect('order_detail', pk=order.pk)