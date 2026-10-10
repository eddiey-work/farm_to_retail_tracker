from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import CropProduce

from accounts.decorators import role_required
from django.db.models import Count, Q

from django.contrib import messages
from django.shortcuts import redirect
from .forms import CropForm

from decimal import Decimal
from django.db import transaction
from orders.models import Order
from .forms import CropForm, OrderForm

from django.core.exceptions import ValidationError

from django.contrib.auth.decorators import login_required


@login_required
def order_confirmation(request, pk):
    """Show the details of a freshly placed order. Owner-only."""
    order = get_object_or_404(
        Order.objects.select_related("crop", "farmer", "retailer"),
        pk=pk,
        retailer=request.user,
    )
    return render(request, "marketplace/order_confirmation.html", {"order": order})


@role_required("retailer")
def place_order(request, pk):
    """Place an order for a crop. Only retailers can order."""
    crop = get_object_or_404(CropProduce.objects.select_related("farmer"), pk=pk)

    # Guard: farmer can't order their own crop (paranoia — role_required already prevents this)
    if crop.farmer == request.user:
        messages.error(request, "You cannot order your own crop.")
        return redirect("crop_detail", pk=crop.pk)

    if not crop.is_available:
        messages.error(request, "This crop is no longer available.")
        return redirect("crop_detail", pk=crop.pk)

    if request.method == "POST":
        form = OrderForm(request.POST, crop=crop)
        if form.is_valid():
            qty = form.cleaned_data["ordered_qty"]
            notes = form.cleaned_data["notes"]

            try:
                with transaction.atomic():
                    # Lock the crop row until this transaction commits
                    locked_crop = CropProduce.objects.select_for_update().get(
                        pk=crop.pk
                    )

                    # Re-check inside the lock
                    if locked_crop.quantity < qty:
                        raise ValidationError(
                            f"Only {locked_crop.quantity} {locked_crop.get_unit_display()} "
                            f"remaining. Someone may have just ordered."
                        )
                    if not locked_crop.is_available:
                        raise ValidationError("This crop is no longer available.")

                    # Compute total using the current price
                    total = (locked_crop.price * qty).quantize(Decimal("0.01"))

                    # Deduct stock
                    locked_crop.quantity -= qty
                    if locked_crop.quantity <= 0:
                        locked_crop.quantity = Decimal("0")
                        locked_crop.is_available = False
                    locked_crop.save()

                    # Create the order
                    order = Order.objects.create(
                        retailer=request.user,
                        farmer=locked_crop.farmer,
                        crop=locked_crop,
                        ordered_qty=qty,
                        total_price=total,
                        notes=notes,
                        status="pending",
                    )

                messages.success(
                    request,
                    f"Order #{order.pk} placed successfully. "
                    f"Waiting for the farmer to confirm.",
                )
                return redirect("order_confirmation", pk=order.pk)

            except ValidationError as e:
                # Raised inside the transaction — the transaction is rolled back automatically
                form.add_error("ordered_qty", e)

        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = OrderForm(crop=crop)

    return render(
        request,
        "marketplace/place_order.html",
        {
            "crop": crop,
            "form": form,
        },
    )


@role_required("farmer")
def crop_delete(request, pk):
    """Confirm and delete a crop. Only the owning farmer can delete."""
    crop = get_object_or_404(CropProduce, pk=pk, farmer=request.user)

    if request.method == "POST":
        name = crop.crop_name
        crop.delete()
        messages.success(request, f"'{name}' has been deleted.")
        return redirect("my_crops")

    return render(request, "marketplace/crop_confirm_delete.html", {"crop": crop})


@role_required("farmer")
def crop_update(request, pk):
    """Edit a crop listing. Only the owning farmer can edit."""
    crop = get_object_or_404(CropProduce, pk=pk, farmer=request.user)

    if request.method == "POST":
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{crop.crop_name}' has been updated.")
            return redirect("my_crops")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CropForm(instance=crop)

    return render(
        request,
        "marketplace/crop_form.html",
        {
            "form": form,
            "page_title": f"Edit {crop.crop_name}",
            "submit_label": "Save changes",
            "crop": crop,
        },
    )


@role_required("farmer")
def crop_create(request):
    """Create a new crop listing for the logged-in farmer."""
    if request.method == "POST":
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.farmer = request.user
            crop.save()
            messages.success(
                request, f"'{crop.crop_name}' has been listed on the marketplace."
            )
            return redirect("my_crops")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CropForm()

    return render(
        request,
        "marketplace/crop_form.html",
        {
            "form": form,
            "page_title": "Add a new crop",
            "submit_label": "List crop",
        },
    )


@role_required("farmer")
def my_crops(request):
    """List the current farmer's own crops with summary stats."""
    crops = CropProduce.objects.filter(farmer=request.user).order_by("-created_at")

    stats = crops.aggregate(
        total=Count("id"),
        available=Count("id", filter=Q(is_available=True)),
        out_of_stock=Count("id", filter=Q(is_available=False)),
    )

    return render(
        request,
        "marketplace/my_crops.html",
        {
            "crops": crops,
            "stats": stats,
        },
    )


def home(request):
    """Landing page — shows a preview of the latest available crops."""
    latest_crops = CropProduce.objects.filter(is_available=True)[:3]
    return render(request, "home.html", {"latest_crops": latest_crops})


def crop_list(request):
    """Public marketplace with search, filter, sort, pagination."""
    crops = CropProduce.objects.filter(is_available=True).select_related("farmer")

    # --- Search by crop name ---
    query = request.GET.get("q", "").strip()
    if query:
        crops = crops.filter(
            Q(crop_name__icontains=query) | Q(description__icontains=query)
        )

    # --- Filter by location ---
    location = request.GET.get("location", "").strip()
    if location:
        crops = crops.filter(location__iexact=location)

    # --- Sort ---
    sort = request.GET.get("sort", "newest")
    sort_map = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_low": "price",
        "price_high": "-price",
    }
    crops = crops.order_by(sort_map.get(sort, "-created_at"))

    # --- Pagination ---
    paginator = Paginator(crops, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # --- For the location filter dropdown ---
    locations = (
        CropProduce.objects.filter(is_available=True)
        .values_list("location", flat=True)
        .distinct()
        .order_by("location")
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "location": location,
        "sort": sort,
        "locations": locations,
        "total_count": crops.count(),
    }
    return render(request, "marketplace/crop_list.html", context)


def crop_detail(request, pk):
    """One crop in full detail."""
    crop = get_object_or_404(
        CropProduce.objects.select_related("farmer", "farmer__profile"), pk=pk
    )
    return render(request, "marketplace/crop_detail.html", {"crop": crop})
