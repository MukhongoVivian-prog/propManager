from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'property_type', 'description', 'location', 'monthly_rent',
                  'wifi', 'parking', 'gym', 'pool', 'security', 'elevator']
