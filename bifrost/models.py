from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomerUser(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  
    password = models.CharField(max_length=128) 
    created_at = models.DateTimeField(auto_now_add=True)


class ConversionRequest(models.Model):
    image = models.ImageField(upload_to='uploads/')
    framework = models.CharField(max_length=50, choices=[
        ('plain', 'Plain HTML/CSS/JS'),
    ])
    output_type = models.CharField(max_length=50, choices=[
        ('full', 'Full Page'),
        ('component', 'Components Only'),
    ])
    css_type = models.CharField(max_length=50, choices=[
        ('regular', 'Regular CSS'),
        ('tailwind', 'Tailwind CSS'),
    ])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_code = models.TextField(blank=True, null=True)

class LoginSession(models.Model):
    user_id = models.IntegerField()
    session_key = models.CharField(max_length=40)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_key} for User {self.user_id}"