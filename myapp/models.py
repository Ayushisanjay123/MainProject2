from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model


# ---------------------------------
# Custom User Manager
# ---------------------------------
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# ---------------------------------
# Custom User Model
# ---------------------------------
class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    role = models.CharField(max_length=20, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

# ---------------------------------
# Agricultural Expertise (moved up since it's used by other models)
# ---------------------------------
class AgriculturalExpertise(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# ---------------------------------
# LandOwner Model (moved before Land model)
# ---------------------------------
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

class LandOwner(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, primary_key=True)
    address = models.TextField(default='', blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Other')
    phone = models.CharField(max_length=15, default='')
    pincode = models.CharField(max_length=10, default='', blank=True)  # ✅ added
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    verified = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    
# ---------------------------------
# LandSeeker Model
# ---------------------------------
class LandSeeker(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=255, null=True)
    photo = models.ImageField(upload_to='seeker_photos/', null=True)
    agricultural_expertise = models.ForeignKey(AgriculturalExpertise, on_delete=models.SET_NULL, null=True)
    crop_requirement = models.CharField(max_length=255, null=True)
    desired_land_size = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    # New fields
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_landseekers'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# ---------------------------------
# Land Model (now properly references LandOwner)
# ---------------------------------
class Land(models.Model):
    owner = models.ForeignKey(LandOwner, on_delete=models.CASCADE, default=1)
    land_name = models.CharField(max_length=100, default="Unnamed Land")  # ← Add this line
    location = models.CharField(max_length=255, default="To be updated")
    size = models.DecimalField(max_digits=10, decimal_places=2)
    water_availability = models.BooleanField(default=False)
    soil_type = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='land_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.land_name  # Changed from location


# ---------------------------------
# UserProfile Model
# ---------------------------------
class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('landowner', 'Land Owner'),
        ('landseeker', 'Land Seeker'),
        ('broker', 'Broker'),
    )
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.user.email} - {self.role}"

# ---------------------------------
# Broker Model
# ---------------------------------
class Broker(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.user.email

# ---------------------------------
# Interest Model
# ---------------------------------
class Interest(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    seeker = models.ForeignKey(LandSeeker, on_delete=models.CASCADE)
    expressed_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('facilitated', 'Facilitated')
    ])

    def __str__(self):
        return f"{self.seeker.user.email} interested in {self.land.location}"

# ---------------------------------
# Agreement Model
# ---------------------------------
class Agreement(models.Model):
    land = models.ForeignKey(Land, on_delete=models.CASCADE)
    landowner = models.ForeignKey(LandOwner, on_delete=models.CASCADE)
    landseeker = models.ForeignKey(LandSeeker, on_delete=models.CASCADE)
    broker = models.ForeignKey(Broker, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    terms = models.TextField()

    def __str__(self):
        return f"Agreement for {self.land.location}"

# ---------------------------------
# Payment Model
# ---------------------------------
class Payment(models.Model):
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_on = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100, default="Cash")

    def __str__(self):
        return f"Payment for {self.agreement.land.location}"

# ---------------------------------
# Report Model
# ---------------------------------
class Report(models.Model):
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    generated_on = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    def __str__(self):
        return f"Report generated by {self.generated_by} on {self.generated_on}"

# ---------------------------------
# Message Model
# ---------------------------------
class Message(models.Model):
    sender = models.ForeignKey(LandSeeker, on_delete=models.CASCADE, null=True, blank=True)
    receiver = models.ForeignKey(LandOwner, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.sent_at}"

# ---------------------------------
# Testimonial Model
# ---------------------------------
class Testimonial(models.Model):
    name = models.CharField(max_length=255)
    feedback = models.TextField()

    def __str__(self):
        return self.name

# ---------------------------------
# FAQ Model
# ---------------------------------
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question

# ---------------------------------
# LandListing Model
# ---------------------------------
class LandListing(models.Model):
    owner = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="land_listings", blank=True, null=True)
    land_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    soil_type = models.CharField(max_length=50, blank=True, null=True)
    water_availability = models.CharField(max_length=100)
    image = models.ImageField(upload_to='land_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)


    def __str__(self):
        return self.land_name
    
    User = get_user_model()

class Notification(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message[:50]}"
    