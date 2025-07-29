from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=200)

    def __str__(self):
        return self.name


# Define choices for the Property Type (should match choices in forms.py)
PROPERTY_TYPE_CHOICES = [
    ('apartment', 'Apartment'),
    ('house', 'House'),
    ('condo', 'Condo'),
    ('townhouse', 'Townhouse'),
    ('studio', 'Studio'),
    ('commercial', 'Commercial'),
    ('other', 'Other'),
]

# Define choices for Amenities (should match choices in forms.py)
# For simplicity, we'll store amenities as a comma-separated string in a CharField.
# For more complex scenarios (many-to-many relationships), a ManyToManyField with a separate Amenity model would be used.
AMENITY_CHOICES = [
    ('wifi', 'WiFi'),
    ('parking', 'Parking'),
    ('gym', 'Gym'),
    ('pool', 'Pool'),
    ('security', 'Security'),
    ('elevator', 'Elevator'),
]


class Property(models.Model):
    """
    Model to store property details, matching the AddPropertyForm fields.
    """
    property_title = models.CharField(max_length=200)
    property_type = models.CharField(
        max_length=50,
        choices=PROPERTY_TYPE_CHOICES,
        default='apartment'  # Set a default value
    )
    description = models.TextField()
    location = models.CharField(max_length=255)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)

    # For amenities, storing as a comma-separated string of selected choices.
    # This is a simple approach for beginners.
    # In a real app, you might use a ManyToManyField or a custom field.
    amenities = models.CharField(
        max_length=200,
        blank=True,  # Allows the field to be empty
        null=True,  # Allows NULL in the database
        help_text="Comma-separated list of amenities (e.g., wifi,pool)"
    )

    # For images, ImageField requires Pillow.
    # You'll also need to configure MEDIA_ROOT and MEDIA_URL in settings.py
    # to handle where these images are stored and served.
    property_image1 = models.ImageField(
        upload_to='property_images/', blank=True, null=True)
    property_image2 = models.ImageField(
        upload_to='property_images/', blank=True, null=True)
    # You can add more ImageFields if you expect a fixed number of images.
    # For truly multiple images, a separate Image model linked by ForeignKey is better.

    # Automatically sets date when created
    date_added = models.DateTimeField(auto_now_add=True)
    # Automatically updates date on each save
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Makes the admin interface show "Properties" instead of "Propertys"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.property_title


# === Abstract Timestamp Model ===
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


# === Custom User Manager ===
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, role=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not role:
            raise ValueError("Role is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email, first_name, last_name, password, role='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# === Custom User Model ===
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('property_manager', 'Property Manager'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ✅ Avoid reverse accessor clashes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"


# === Property Model ===
class Property(TimeStampedModel):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('bedsitter', 'Bedsitter'),
        ('studio', 'Studio'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    property_type = models.CharField(
        max_length=20, choices=PROPERTY_TYPE_CHOICES)
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    image = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False)
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties',
                                 default=None, limit_choices_to={'role': 'landlord'})

    def __str__(self):
        return self.title


# === Tenant Profile ===
class TenantProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='tenant_profile')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile for {self.user.email}"


# === Booking Model ===
class Booking(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='bookings', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.property.title} - {self.tenant.email}"


# === Review Model ===
class Review(TimeStampedModel):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='reviews', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.tenant.email} for {self.property.title}"


# === Favorite Model ===
class Favorite(TimeStampedModel):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='favorites', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ('tenant', 'property')

    def __str__(self):
        return f"{self.tenant.email} likes {self.property.title}"
