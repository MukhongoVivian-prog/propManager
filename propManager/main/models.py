from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

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
        user = self.create_user(email, first_name, last_name, password, role='admin')
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

    #Avoid reverse accessor clashes
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
    PROPERTY_STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Booked', 'Booked'),
]


    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    description = models.TextField()
    location = models.CharField(max_length=100)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PROPERTY_STATUS_CHOICES, default='Available')
    wifi = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    gym = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    security = models.BooleanField(default=False)
    elevator = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties', default=None, limit_choices_to={'role': 'landlord'})

    def __str__(self):
        return self.title


# === Tenant Profile ===
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Profile for {self.user.email}"


class Booking(TimeStampedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.property.title} - {self.tenant.email}"


# === Review Model ===
class Review(TimeStampedModel):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    def __str__(self):
        return f"Review by {self.tenant.email} for {self.property.title}"


# === Favorite Model ===
class Favorite(TimeStampedModel):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', limit_choices_to={'role': 'tenant'})
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ('tenant', 'property')

    def __str__(self):
        return f"{self.tenant.email} likes {self.property.title}"


# model to handle the landlord features

PROPERTY_TYPE_CHOICES = [
    ('Apartment', 'Apartment'),
    ('Bedsitter', 'Bedsitter'),
    ('Condo', 'Condo'),
]

PROPERTY_STATUS_CHOICES = [
    ('Available', 'Available'),
    ('Booked', 'Booked'),
]

TENANT_STATUS_CHOICES = [
    ('Interested', 'Interested'),
    ('Booked', 'Booked'),
]



class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')


class TenantInteraction(models.Model):
    tenant_name = models.CharField(max_length=100)
    tenant_email = models.EmailField()
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    view_date = models.DateField()
    status = models.CharField(max_length=20, choices=TENANT_STATUS_CHOICES)

    def __str__(self):
        return f"{self.tenant_name} - {self.property.title}"



