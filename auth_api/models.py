from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_admin", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # remove the default username field
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=11, blank=True, null=True)
    region = models.CharField(max_length=200,default="unknown")

    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    


class CustomUser(models.Model):


    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=200,
        default='incompleted'
    )
    region = models.CharField(
        max_length=200,
        default='Unknown',  
        blank=True
    )

    

     

    def __str__(self):
        return f"{self.user.email} - {self.status} - {self.region}"


class UserProfile(models.Model):
    rider = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rides_as_rider', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='rides_as_user', on_delete=models.CASCADE)
    pickup = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    requested_at = models.DateTimeField()
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ride {self.id} by {self.user} accepted by {self.rider}"
    

class UerOTP(models.Model):
    email = models.CharField()
    otp = models.CharField(max_length=6)    





import uuid

class SignupRequest(models.Model):

    STATUS_CHOICES = (
        ('pending','Pending'),
        ('success','Success'),
        ('failed','Failed')
    )

    request_id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    username = None  # remove the default username field
    email = models.EmailField(unique=True,default=None)
    full_name = models.CharField(max_length=255,default=None)
    mobile_no = models.CharField(max_length=11, blank=True, null=True,default=None)
    region = models.CharField(max_length=200,default="unknown")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.status}"


