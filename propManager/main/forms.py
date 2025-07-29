from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from main.models import Contact


class ContactForms(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }


# chat_app/forms.py

# Define choices for the Property Type dropdown
PROPERTY_TYPE_CHOICES = [
    ('', 'Select type'),  # Empty choice for placeholder
    ('apartment', 'Apartment'),
    ('house', 'House'),
    ('condo', 'Condo'),
    ('townhouse', 'Townhouse'),
    ('studio', 'Studio'),
    ('commercial', 'Commercial'),
    ('other', 'Other'),
]

# Define choices for Amenities checkboxes
AMENITY_CHOICES = [
    ('wifi', 'WiFi'),
    ('parking', 'Parking'),
    ('gym', 'Gym'),
    ('pool', 'Pool'),
    ('security', 'Security'),
    ('elevator', 'Elevator'),
]


class AddPropertyForm(forms.Form):
    """
    A Django form for adding a new property, based on the provided image fields.
    """
    property_title = forms.CharField(
        label="Property Title",
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Enter property title'})
    )

    property_type = forms.ChoiceField(
        label="Property Type",
        choices=PROPERTY_TYPE_CHOICES,
        required=True,  # Make selection mandatory
        # Add a class for styling
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            # Multi-line input
            attrs={'placeholder': 'Describe your property', 'rows': 4})
    )

    location = forms.CharField(
        label="Location",
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Property location'})
    )

    monthly_rent = forms.DecimalField(  # Use DecimalField for currency
        label="Monthly Rent",
        min_value=0.01,
        max_digits=10,  # Max total digits
        decimal_places=2,  # Digits after decimal point
        widget=forms.NumberInput(attrs={'placeholder': 'Enter rent amount'})
    )

    # MultipleChoiceField with CheckboxSelectMultiple for amenities
    amenities = forms.MultipleChoiceField(
        label="Amenities",
        choices=AMENITY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False  # Amenities are optional
    )

    # File input for multiple images
    # Note: For actual file uploads, you'll need to handle request.FILES in your view
    # and configure MEDIA_ROOT/MEDIA_URL in settings.py.
    property_images = forms.FileField(
        label="Property Images",
        # Allows selecting multiple files
        widget=forms.ClearableFileInput(attrs={'multiple': False}),
        required=False,  # Images are optional
        help_text="Drag and drop images or click to upload."
    )
