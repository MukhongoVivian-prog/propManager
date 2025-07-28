from django.contrib import admin
from .models import User, Property, Booking, Review, Favorite, Profile, PropertyImage, TenantInteraction     

admin.site.register(User)
admin.site.register(Property)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(Profile)
admin.site.register(PropertyImage)
admin.site.register(TenantInteraction)


