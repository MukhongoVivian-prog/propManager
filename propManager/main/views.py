from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Property, Booking, Review, Favorite, TenantProfile, User
from django.views.decorators.csrf import csrf_protect


def index(request):
    return render(request, 'index.html')


@csrf_protect
def register_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm = request.POST.get('confirmPassword')

        if not all([role, first_name, last_name, email, password, confirm]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role
        )
        user.phone = phone
        user.save()

        if role == 'tenant':
            TenantProfile.objects.create(user=user, phone=phone)

        messages.success(request, "Account created. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not all([email, password, role]):
            messages.error(request, "All fields are required.")
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.role != role:
                messages.error(request, "Incorrect role selected.")
                return redirect('login')

            login(request, user)
            # ✅ Redirect user based on their role
            if user.role == 'tenant':
                return redirect('tenant_dashboard')
            elif user.role == 'landlord':
                return redirect('landlord_dashboard')
            elif user.role == 'property_manager':
                return redirect('manager_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  # Django admin site

        messages.error(request, "Invalid credentials.")
        return redirect('login')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


# === Tenant Views ===
@login_required
def tenant_dashboard(request):
    if request.user.role != 'tenant':
        messages.error(request, "Access denied.")
        return redirect('login')

    properties = Property.objects.all()
    context = {
        'user': request.user,
        'properties': properties,
        'active_page': 'browse',
    }
    return render(request, 'tenant_dashboard.html', context)


@login_required
def tenant_bookings(request):
    if request.user.role != 'tenant':
        messages.error(request, "Access denied.")
        return redirect('login')

    bookings = Booking.objects.filter(tenant=request.user).order_by('-date')
    context = {
        'bookings': bookings,
        'active_page': 'bookings',
    }
    return render(request, 'tenant_bookings.html', context)


@login_required
def tenant_reviews(request):
    if request.user.role != 'tenant':
        messages.error(request, "Access denied.")
        return redirect('login')

    reviews = Review.objects.filter(tenant=request.user).order_by('-created_at')
    context = {
        'reviews': reviews,
        'active_page': 'reviews',
    }
    return render(request, 'tenant_reviews.html', context)


@login_required
def tenant_favorites(request):
    if request.user.role != 'tenant':
        messages.error(request, "Access denied.")
        return redirect('login')

    favorites = Favorite.objects.filter(tenant=request.user).select_related('property').order_by('-created_at')
    context = {
        'favorites': favorites,
        'active_page': 'favorites',
    }
    return render(request, 'tenant_favorites.html', context)


@login_required
def tenant_settings(request):
    if request.user.role != 'tenant':
        messages.error(request, "Access denied.")
        return redirect('login')

    user = request.user
    profile, _ = TenantProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        profile.phone = request.POST.get('phone', profile.phone)

        user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('tenant_settings')

    context = {
        'user': user,
        'profile': profile,
        'active_page': 'settings',
    }
    return render(request, 'tenant_settings.html', context)
