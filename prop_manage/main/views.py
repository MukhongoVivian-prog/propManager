from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Property, Booking, Review, Favorite, Profile, PropertyImage, TenantInteraction
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.db import IntegrityError
from .models import User
from .forms import PropertyForm
from .forms import BookingForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

# Create your views here.


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


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

        # Set is_staff for admin users
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True

        user.save()

        if role == 'tenant':
            Profile.objects.create(user=user, phone=phone)
        elif role == 'landlord':
            Profile.objects.create(user=user, phone=phone)

        messages.success(request, "Account created. You can now log in.")
        return redirect('login')

    return render(request, 'register.html')


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
            # Redirect user based on their role
            if user.role == 'tenant':
                return redirect('tenant_dashboard')
            elif user.role == 'landlord':
                return redirect('landlord_dashboard')
            elif user.role == 'admin':
                return redirect('/admin/')  # Django admin site

        messages.error(request, "Invalid credentials.")
        return redirect('login')

    return render(request, 'login.html')


def terms(request):
    return render(request, 'terms.html')


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
    reviews = Review.objects.filter(
        tenant=request.user).order_by('-created_at')
    context = {
        'user': request.user,
        'reviews': reviews,
        'active_page': 'reviews',
    }
    return render(request, 'tenant_reviews.html', context)


@login_required
def tenant_favorites(request):
    favorites = Favorite.objects.filter(tenant=request.user).select_related(
        'property').order_by('-created_at')
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
    properties = Property.objects.filter(
        landlord=request.user).annotate(bookings_count=Count('bookings'))
    total_properties = properties.count()
    monthly_revenue = properties.aggregate(
        total=Sum('monthly_rent'))['total'] or 0
    active_tenants = TenantInteraction.objects.filter(
        property__in=properties, status='Booked').count()
    occupancy_rate = int((active_tenants / total_properties)
                         * 100) if total_properties else 0

    context = {
        'total_properties': total_properties,
        'monthly_revenue': monthly_revenue,
        'active_tenants': active_tenants,
        'occupancy_rate': occupancy_rate,
        'properties': properties,
        'active_page': 'overview',
        'user': request.user,
    }
    return render(request, 'landlord_dashboard.html', context)


@login_required
def landlord_bookings(request):
    properties = Property.objects.filter(landlord=request.user)
    bookings = Booking.objects.filter(property__in=properties).select_related(
        'tenant', 'property').order_by('-date')
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        booking = Booking.objects.filter(
            id=booking_id, property__in=properties).first()
        if booking:
            if action == 'approve':
                booking.status = 'confirmed'
                booking.save()
                messages.success(
                    request, f'Booking for {booking.property.title} approved.')
            elif action == 'reject':
                booking.status = 'cancelled'
                booking.save()
                messages.success(
                    request, f'Booking for {booking.property.title} rejected.')
        return redirect('landlord_bookings')
    return render(request, 'landlord_bookings.html', {
        'bookings': bookings,
        'user': request.user,
        'active_page': 'bookings',
    })


@login_required
def tenant_interactions(request):
    properties = Property.objects.filter(landlord=request.user)
    interactions = TenantInteraction.objects.filter(property__in=properties)
    return render(request, 'view_tenants.html', {
        'interactions': interactions,
        'active_page': 'tenants',
        'user': request.user,
    })


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property = form.save(commit=False)
            property.landlord = request.user
            property.save()
            for file in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=property, image=file)
            messages.success(
                request, f'Property "{property.title}" has been added successfully!')
            return redirect('landlord_dashboard')
    else:
        form = PropertyForm()
    return render(request, 'add_property.html', {'form': form, 'active_page': 'add_property', 'user': request.user})


@login_required
def landlord_settings(request):
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
        return redirect('landlord_settings')
    context = {
        'user': user,
        'profile': profile,
        'active_page': 'settings',
    }
    return render(request, 'landlord_settings.html', context)


@login_required
def view_property(request, property_id):
    property = get_object_or_404(
        Property, id=property_id, landlord=request.user)
    return render(request, 'property_details.html', {'property': property, 'user': request.user})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')  # Or redirect to 'index' if preferred\


def sidebar():
    return render(request, 'landlord_sidebar.html')


@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    booking_success = False
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tenant = request.user
            booking.property = property
            booking.price = property.monthly_rent
            booking.status = 'pending'
            booking.save()

            # Send email to tenant
            tenant_subject = f'Booking Confirmation - {property.title}'
            tenant_html_message = render_to_string('emails/booking_confirmation_tenant.html', {
                'booking': booking,
                'property': property,
                'tenant': request.user,
            })
            tenant_plain_message = strip_tags(tenant_html_message)
            send_mail(
                tenant_subject,
                tenant_plain_message,
                'noreply@propmanager.com',
                [request.user.email],
                html_message=tenant_html_message,
                fail_silently=False,
            )

            # Send email to landlord
            landlord_subject = f'New Booking Request - {property.title}'
            landlord_html_message = render_to_string('emails/booking_notification_landlord.html', {
                'booking': booking,
                'property': property,
                'tenant': request.user,
            })
            landlord_plain_message = strip_tags(landlord_html_message)
            send_mail(
                landlord_subject,
                landlord_plain_message,
                'noreply@propmanager.com',
                [property.landlord.email],
                html_message=landlord_html_message,
                fail_silently=False,
            )

            messages.success(
                request, 'Booking request submitted! Check your email for confirmation.')
            booking_success = True
    else:
        form = BookingForm()
    return render(request, 'property_detail.html', {
        'property': property,
        'form': form,
        'booking_success': booking_success,
        'active_page': 'browse',
        'user': request.user,
    })


@login_required
def reserve_booking(request, booking_id):
    """Reserve a pending booking"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if booking.status == 'pending':
        booking.status = 'reserved'
        booking.save()

        # Send confirmation email
        subject = f'Booking Reserved - {booking.property.title}'
        html_message = render_to_string('emails/booking_reserved.html', {
            'booking': booking,
            'property': booking.property,
            'tenant': request.user,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            'noreply@propmanager.com',
            [request.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            request, f'Booking for {booking.property.title} has been reserved!')
        return redirect('booking_success', booking_id=booking.id)
    else:
        messages.error(request, 'Invalid booking status for reservation.')
        return redirect('tenant_bookings')


@login_required
def landlord_approve_booking(request, booking_id):
    """Landlord approves a pending booking"""
    booking = get_object_or_404(
        Booking, id=booking_id, property__landlord=request.user)
    if booking.status == 'pending':
        booking.status = 'approved'
        booking.landlord_approved = True
        booking.save()

        # Send approval email to tenant
        subject = f'Booking Approved - {booking.property.title}'
        html_message = render_to_string('emails/booking_approved.html', {
            'booking': booking,
            'property': booking.property,
            'tenant': booking.tenant,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            'noreply@propmanager.com',
            [booking.tenant.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            request, f'Booking for {booking.property.title} has been approved.')
        return redirect('landlord_bookings')
    else:
        messages.error(request, 'Invalid booking status for approval.')
        return redirect('landlord_bookings')


@login_required
def payment_page(request, booking_id):
    """Payment page for approved bookings"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if booking.status == 'approved':
        return render(request, 'payment_page.html', {
            'booking': booking,
            'property': booking.property,
            'user': request.user,
        })
    else:
        messages.error(request, 'Booking must be approved before payment.')
        return redirect('tenant_bookings')


@login_required
def process_payment(request, booking_id):
    """Process payment for booking"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if booking.status == 'approved' and request.method == 'POST':
        # Simulate payment processing
        booking.status = 'payment_completed'
        booking.payment_status = 'completed'
        booking.payment_date = timezone.now()
        booking.save()

        # Send payment confirmation email
        subject = f'Payment Confirmed - {booking.property.title}'
        html_message = render_to_string('emails/payment_confirmed.html', {
            'booking': booking,
            'property': booking.property,
            'tenant': request.user,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            'noreply@propmanager.com',
            [request.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            request, 'Payment completed successfully! You can now check in.')
        return redirect('payment_success', booking_id=booking.id)
    else:
        messages.error(request, 'Invalid booking status for payment.')
        return redirect('tenant_bookings')


@login_required
def payment_success(request, booking_id):
    """Payment success page"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    return render(request, 'payment_success.html', {
        'booking': booking,
        'property': booking.property,
        'user': request.user,
    })


@login_required
def checkin_booking(request, booking_id):
    """Check in to a payment completed booking"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    if booking.status == 'payment_completed':
        booking.status = 'checked_in'
        booking.save()

        # Send checkin confirmation email
        subject = f'Check-in Confirmed - {booking.property.title}'
        html_message = render_to_string('emails/checkin_confirmation.html', {
            'booking': booking,
            'property': booking.property,
            'tenant': request.user,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            'noreply@propmanager.com',
            [request.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            request, f'Successfully checked in to {booking.property.title}!')
        return redirect('booking_success', booking_id=booking.id)
    else:
        messages.error(request, 'Payment must be completed before check-in.')
        return redirect('tenant_bookings')


@login_required
def booking_success(request, booking_id):
    """Show booking success page"""
    booking = get_object_or_404(Booking, id=booking_id, tenant=request.user)
    return render(request, 'booking_success.html', {
        'booking': booking,
        'property': booking.property,
        'user': request.user,
    })


def edit_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, instance=property)
        if form.is_valid():
            form.save()
            return redirect('property_detail', pk=property.pk)
    else:
        form = PropertyForm(instance=property)
    return render(request, 'edit_property.html', {'form': form})


def delete_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property.delete()
        return redirect('dashboard')  # or whatever list page
    return render(request, 'confirm_delete.html', {'object': property})


@login_required
def browse_properties(request):
    properties = Property.objects.filter(status='Available')
    return render(request, 'browse_properties.html', {
        'properties': properties,
        'active_page': 'browse',
        'user': request.user,
    })


def properties(request):
    """Public properties page - shows basic property details"""
    properties = Property.objects.filter(status='Available')[
        :6]  # Show first 6 available properties
    return render(request, 'properties.html', {
        'properties': properties,
    })
