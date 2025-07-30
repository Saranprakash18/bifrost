from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
import uuid
from django.utils.html import format_html

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
    


class UploadHistory(models.Model):
    FRAMEWORK_CHOICES = [
        ('plain', 'Plain HTML/CSS/JS'),
        ('bootstrap', 'Bootstrap'),
        ('tailwind', 'Tailwind CSS'),
    ]
    
    CSS_STYLE_CHOICES = [
        ('inline', 'Inline Styles'),
        ('external', 'External CSS'),
        ('css_modules', 'CSS Modules'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cloud_image_url = models.URLField(max_length=500)
    framework_type = models.CharField(max_length=50, choices=FRAMEWORK_CHOICES, default='plain')
    css_style = models.CharField(max_length=50, choices=CSS_STYLE_CHOICES, default='external')
    created_at = models.DateTimeField(auto_now_add=True)
    html_code = models.TextField()
    css_code = models.TextField()
    js_code = models.TextField()
    ocr_text = models.TextField()

    def __str__(self):
        return f"{self.user.username}'s upload on {self.created_at.strftime('%Y-%m-%d')}"

    def uploaded_image_display(self):
        # /upload/ with Cloudinary thumbnail transformation
        if "/upload/" in self.cloud_image_url:
            thumb_url = self.cloud_image_url.replace("/upload/", "/upload/w_100,h_100,c_fill/")
        else:
            thumb_url = self.cloud_image_url  # fallback if URL format changes

        return format_html('<img src="{}" width="100" style="border:1px solid #ddd; border-radius:6px"/>', thumb_url)

    uploaded_image_display.short_description = 'Uploaded Image'