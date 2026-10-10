from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, LoginForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account is ready.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Please fill in both fields.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    """Send farmers and retailers to their own dashboard with stats."""
    profile = request.user.profile

    if profile.role == 'farmer':
        from marketplace.models import CropProduce
        from orders.models import Order
        from django.db.models import Q, Count

        crops = CropProduce.objects.filter(farmer=request.user)
        orders = Order.objects.filter(farmer=request.user)

        context = {
            'crop_count': crops.count(),
            'out_of_stock_count': crops.filter(is_available=False).count(),
            'order_count': orders.count(),
        }
        return render(request, 'accounts/dashboard_farmer.html', context)

    elif profile.role == 'retailer':
        from orders.models import Order

        orders = Order.objects.filter(retailer=request.user)
        context = {
            'order_count': orders.count(),
            'pending_count': orders.filter(status='pending').count(),
            'confirmed_count': orders.filter(status='confirmed').count(),
        }
        return render(request, 'accounts/dashboard_retailer.html', context)

    else:
        messages.error(request, "Unknown role. Contact support.")
        return redirect('home')