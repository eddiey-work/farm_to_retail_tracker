from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from .models import CropProduce

from accounts.decorators import role_required
from django.db.models import Count, Q


@role_required('farmer')
def my_crops(request):
    """List the current farmer's own crops with summary stats."""
    crops = (
        CropProduce.objects
        .filter(farmer=request.user)
        .order_by('-created_at')
    )

    stats = crops.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(is_available=True)),
        out_of_stock=Count('id', filter=Q(is_available=False)),
    )

    return render(request, 'marketplace/my_crops.html', {
        'crops': crops,
        'stats': stats,
    })

def home(request):
    """Landing page — shows a preview of the latest available crops."""
    latest_crops = CropProduce.objects.filter(is_available=True)[:3]
    return render(request, 'home.html', {'latest_crops': latest_crops})


def crop_list(request):
    """Public marketplace with search, filter, sort, pagination."""
    crops = CropProduce.objects.filter(is_available=True).select_related('farmer')

    # --- Search by crop name ---
    query = request.GET.get('q', '').strip()
    if query:
        crops = crops.filter(
            Q(crop_name__icontains=query) |
            Q(description__icontains=query)
        )

    # --- Filter by location ---
    location = request.GET.get('location', '').strip()
    if location:
        crops = crops.filter(location__iexact=location)

    # --- Sort ---
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'price',
        'price_high': '-price',
    }
    crops = crops.order_by(sort_map.get(sort, '-created_at'))

    # --- Pagination ---
    paginator = Paginator(crops, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- For the location filter dropdown ---
    locations = (
        CropProduce.objects.filter(is_available=True)
        .values_list('location', flat=True)
        .distinct()
        .order_by('location')
    )

    context = {
        'page_obj': page_obj,
        'query': query,
        'location': location,
        'sort': sort,
        'locations': locations,
        'total_count': crops.count(),
    }
    return render(request, 'marketplace/crop_list.html', context)


def crop_detail(request, pk):
    """One crop in full detail."""
    crop = get_object_or_404(
        CropProduce.objects.select_related('farmer', 'farmer__profile'),
        pk=pk
    )
    return render(request, 'marketplace/crop_detail.html', {'crop': crop})