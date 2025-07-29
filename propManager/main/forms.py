from django import forms
from .models import Property, Booking, Review


class PropertyForm(forms.ModelForm):
    images = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        required=False,
        help_text='Upload images for the property (you can select multiple files)'
    )
    
    class Meta:
        model = Property
        fields = ['title', 'property_type', 'description', 'location', 'monthly_rent', 'status', 'wifi', 'parking', 'gym', 'pool', 'security', 'elevator']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter property title'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your property'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property location'}),
            'monthly_rent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter rent amount'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'elevator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }