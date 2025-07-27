from django.shortcuts import render
from main.forms import ContactForms
from django.shortcuts import render, redirect
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
import json
# import requests
from django.urls import path
from main.forms import AddPropertyForm


# Create your views here.
def index(request):
    return render(request, 'index.html')

def contact(request):
    form = ContactForms()
    if request.method == 'POST':
        form = ContactForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    return render(request, 'contact.html', {'form': form})

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
def properties(request):
    # This view would typically fetch properties from the database
    # For now, we'll just return an empty context
    return render(request, 'properties.html')



# # chat bot
# # chat_app/views.py
# # For making HTTP requests to Gemini API

# # Chat history to maintain context for the LLM
# # In a real application, this would be stored per user in a database or session
# # For simplicity, we'll keep a global history for this example.
# chat_history = []

# # --- Gemini API Configuration ---
# # IMPORTANT: Leave apiKey as an empty string. The Canvas environment will inject it.
# GEMINI_API_KEY = ""
# GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# # View to render the chat interface
# def chat_view(request):
#     return render(request, 'chat_app/chat.html')

# # View to handle sending messages and getting bot responses
# @csrf_exempt # This decorator is needed to exempt this view from CSRF protection for AJAX POST requests
#              # For production, consider using {% csrf_token %} in form and django.middleware.csrf.CsrfViewMiddleware
# def send_message(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             user_message = data.get('message')

#             if not user_message:
#                 return JsonResponse({'error': 'No message provided'}, status=400)

#             # Add user message to chat history
#             chat_history.append({"role": "user", "parts": [{"text": user_message}]})

#             # Prepare payload for Gemini API
#             payload = {
#                 "contents": chat_history, # Send the entire history for context
#                 "generationConfig": {
#                     "temperature": 0.7, # Controls randomness. Lower = more deterministic
#                     "maxOutputTokens": 150 # Limit response length
#                 }
#             }

#             headers = {'Content-Type': 'application/json'}
            
#             # Make the API call to Gemini
#             response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
#             response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
#             gemini_result = response.json()

#             bot_response = "I'm sorry, I couldn't generate a response."
#             if gemini_result.get('candidates') and gemini_result['candidates'][0].get('content'):
#                 # Extract text from the response
#                 bot_response = gemini_result['candidates'][0]['content']['parts'][0]['text']
            
#             # Add bot response to chat history
#             chat_history.append({"role": "model", "parts": [{"text": bot_response}]})

#             return JsonResponse({'response': bot_response})

#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         except requests.exceptions.RequestException as e:
#             print(f"Error calling Gemini API: {e}")
#             return JsonResponse({'error': f'Failed to connect to AI service: {e}'}, status=500)
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#             return JsonResponse({'error': 'An internal server error occurred.'}, status=500)
    
#     return JsonResponse({'error': 'Invalid request method'}, status=405)






def add_property(request):
    if request.method == 'POST':
        form = AddPropertyForm(request.POST, request.FILES) # Pass request.FILES for file uploads
        if form.is_valid():
            # Process the data
            # For example, you can access cleaned data:
            # title = form.cleaned_data['property_title']
            # description = form.cleaned_data['description']
            # images = form.cleaned_data['property_images'] # This will be a list of UploadedFile objects

            # Here you would typically save the data to your models
            # e.g., Property.objects.create(...)

            # For now, let's just print it to the console
            print("Form is valid!")
            # print(form.cleaned_data)

            # Redirect to a success page or back to the same page
            return redirect('add_property_success') # You'd define this URL in urls.py
        else:
            # Form is not valid, it will re-render with errors
            print("Form is NOT valid!")
            print(form.errors) # Print errors for debugging
    else:
        form = AddPropertyForm() # Create an empty form for GET requests

    return render(request, 'add_property.html', {'form': form})