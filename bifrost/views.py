import easyocr
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from bifrost.models import ConversionRequest
from cloudinary_storage.storage import MediaCloudinaryStorage
from .models import UploadHistory
import uuid
from django.core.files.storage import default_storage
import os
import tempfile
import cv2
import numpy as np
from bifrost.image_processor import (
    process_uploaded_image
)
import traceback
from django.conf import settings
import tempfile

# Home page
def index(request):
    return render(request, 'frontend/index.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Kindly fill all the fields.")
            return redirect('login')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email ID doesn't exist.")
            return redirect('login')

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session.set_expiry(0)  # Session expires on browser close
            messages.success(request, "Login successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'frontend/login.html')

# Signup view
def signup(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname", "").strip()
        lastname = request.POST.get("lastname", "").strip()
        username = request.POST.get("username")
        fullname = f"{firstname} {lastname}"
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirmPassword", "")
        terms = request.POST.get("terms", "")

        if not all([firstname, lastname, username, email, password, confirm_password, terms]):
            messages.error(request, "Kindly fill the form")
            return render(request, "frontend/signup.html")

        if password != confirm_password:
            messages.error(request, "Password didn't match")
            return render(request, "frontend/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "frontend/signup.html")

        user = User.objects.create_user(
            first_name=firstname,
            last_name=lastname,
            username=username,
            email=email,
            password=password
        )
        auth_login(request, user)
        request.session.set_expiry(0)  #Session expires on browser close
        messages.success(request, "Account created successfully. You are now logged in.")
        return redirect('dashboard')

    return render(request, "frontend/signup.html")

# Dashboard view (protected & never cached)
@never_cache
@login_required(login_url='login')
def dashboard(request):
    if request.method == 'POST':
        image = request.FILES['image']
        framework = request.POST['framework']
        output_type = request.POST['output_type']
        css_type = request.POST['css_type']

        entry = ConversionRequest.objects.create(
            image=image,
            framework=framework,
            output_type=output_type,
            css_type=css_type
        )

        reader = easyocr.Reader(['en'])
        result = reader.readtext(entry.image.path)
        text_output = "\n".join([r[1] for r in result])

        entry.extracted_code = text_output
        entry.save()

        return redirect('view_result', pk=entry.pk)

    return render(request, 'frontend/dashboard.html')

# Other simple views
def templates(request):
    return render(request, 'frontend/templates.html')

def history(request):
    uploads = UploadHistory.objects.filter(user=request.user).order_by('-created_at')

    for upload in uploads:
        # Inject a new field 'thumbnail_url' using Cloudinary transformations
        original_url = upload.cloud_image_url
        if "/upload/" in original_url:
            # 300x200, auto crop/fit
            thumbnail_url = original_url.replace("/upload/", "/upload/w_300,h_200,c_fit/")
        else:
            thumbnail_url = original_url  # fallback in case Cloudinary format changes
        upload.thumbnail_url = thumbnail_url  # dynamically attach

    context = {
        'uploads': uploads,
        'has_uploads': uploads.exists()
    }
    return render(request, 'frontend/history.html', context)

def help(request):
    return render(request, 'frontend/help.html')

@login_required(login_url='login')
def profile(request):
    return render(request, 'frontend/profile.html', {
        'user': request.user,
    })

# Secure logout
def user_logout(request):
    request.session.flush()  # Clears session from DB + browser
    logout(request)          # Logs out Django user
    return redirect('/')

@login_required
def handle_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        framework = request.POST.get('framework', 'vanilla')
        css_type = request.POST.get('css_type', 'external')

        # Input validation
        if framework not in ['vanilla', 'react']:
            framework = 'vanilla'
        if css_type not in ['external', 'inline']:
            css_type = 'external'

        temp_path = None

        try:
            # Save file temporarily
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # Read image
            image = cv2.imread(temp_path)
            if image is None:
                messages.error(request, "Invalid image file")
                return redirect('dashboard')

            # 🔥 One-stop image processing
            processed = process_uploaded_image(temp_path, framework, css_type)

            # Upload to Cloudinary
            cloud_storage = MediaCloudinaryStorage()
            username = request.user.username
            cloud_filename = f"user_uploads/{username}_{uploaded_file.name}"
            
            with open(temp_path, 'rb') as f:
                cloudinary_file = cloud_storage.save(cloud_filename, f)
                cloud_url = cloud_storage.url(cloudinary_file)

            # Save to database
            upload = UploadHistory.objects.create(
                user=request.user,
                cloud_image_url=cloud_url,
                html_code=processed["html_code"],
                css_code="",  # If you want to store CSS/JS, return them from process_uploaded_image()
                js_code="",
                framework_type=framework,
                css_style=css_type,
                ocr_text="\n".join([t['text'] for t in processed['texts']])
            )

            return redirect('result_page', upload_id=upload.id)

        except Exception as e:
            traceback.print_exc()
            messages.error(request, f"Processing error: {str(e)}")
            return redirect('dashboard')

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    print(f"Error deleting temp file: {e}")

    messages.error(request, "No image uploaded")
    return redirect('dashboard')

    
@login_required
def result_page(request, upload_id):
    try:
        upload = UploadHistory.objects.get(id=upload_id, user=request.user)
        return render(request, 'frontend/result.html', {
            'html_code': upload.html_code,
            'css_code': upload.css_code,
            'js_code': upload.js_code,
            'image_url': upload.cloud_image_url
        })
    except UploadHistory.DoesNotExist:
        messages.error(request, "Result not found")
        return redirect('dashboard')