from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, Booking, Review, Favorite, Profile, PropertyImage, TenantInteraction
from django.db.models import Sum
from django.shortcuts import get_object_or_404  
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from .models import User
from .forms import PropertyForm

# Create your views here.
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
            Profile.objects.create(user=user, phone=phone)
        elif role == 'landlord':
            Profile.objects.create(user=user, phone=phone)

        messages.success(request, "Account created. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')

    
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
def tenant_dashboard(request):
    properties = Property.objects.all()
    context = {
        'user': request.user,
        'properties': properties,
        'active_page': 'browse',
    }
    return render(request, 'tenant_dashboard.html', context)

@login_required
def tenant_bookings(request):
    bookings = Booking.objects.filter(tenant=request.user).order_by('-date')
    context = {
        'user': request.user,
        'bookings': bookings,
        'active_page': 'bookings',
    }
    return render(request, 'tenant_bookings.html', context)

@login_required
def tenant_reviews(request):
    reviews = Review.objects.filter(tenant=request.user).order_by('-created_at')
    context = {
        'user': request.user,
        'reviews': reviews,
        'active_page': 'reviews',
    }
    return render(request, 'tenant_reviews.html', context)

@login_required
def tenant_favorites(request):
    favorites = Favorite.objects.filter(tenant=request.user).select_related('property').order_by('-created_at')
    context = {
        'user': request.user,
        'favorites': favorites,
        'active_page': 'favorites',
    }
    return render(request, 'tenant_favorites.html', context)

@login_required
def tenant_settings(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
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

# landlord views

@login_required
def landlord_dashboard(request):
    properties = Property.objects.filter(landlord=request.user)
    total_properties = properties.count()
    monthly_revenue = properties.aggregate(total=Sum('monthly_rent'))['total'] or 0
    active_tenants = TenantInteraction.objects.filter(property__in=properties, status='Booked').count()
    occupancy_rate = int((active_tenants / total_properties) * 100) if total_properties else 0

    context = {
        'total_properties': total_properties,
        'monthly_revenue': monthly_revenue,
        'active_tenants': active_tenants,
        'occupancy_rate': occupancy_rate,
        'properties': properties,
    }
    return render(request, 'landlord_dashboard.html', context)


@login_required
def tenant_interactions(request):
    properties = Property.objects.filter(landlord=request.user)
    interactions = TenantInteraction.objects.filter(property__in=properties)

    return render(request, 'view_tenants.html', {
        'interactions': interactions
    })


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            property.save()
            # Save multiple images if supported
            for file in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=property, image=file)
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form})


@login_required
def view_property(request, property_id):
    property = get_object_or_404(Property, id=property_id, landlord=request.user)
    return render(request, 'property_details.html', {'property': property})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Or redirect to 'index' if preferred\

def sidebar():
    return render(request, 'landlord_siebar.html')