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
    context = {
        'uploads': uploads,
        'has_uploads': uploads.exists()
    }
    return render(request, 'frontend/history.html',context)

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
    if request.method == 'POST':
        # Get form data
        uploaded_file = request.FILES.get('image')
        framework = request.POST.get('framework', 'vanilla')
        css_type = request.POST.get('css_type', 'external')
        
        if not uploaded_file:
            messages.error(request, "Please upload an image")
            return redirect('dashboard')

        # Generate unique filename for Cloudinary
        unique_id = str(uuid.uuid4())[:8]
        cloud_filename = f"{request.user.username}_{unique_id}.png"

        # Save to Cloudinary
        cloud_storage = MediaCloudinaryStorage()
        cloudinary_file = cloud_storage.save(cloud_filename, uploaded_file)
        cloud_url = cloud_storage.url(cloudinary_file)

        # Process image with OpenCV and EasyOCR
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # Read image
            image = cv2.imread(temp_path)
            if image is None:
                raise ValueError("Could not read image file")

            # Initialize OCR reader
            reader = easyocr.Reader(['en'])

            # Preprocess image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Generate HTML/CSS from detected elements
            html_elements = []
            css_elements = []
            ocr_texts = []

            for idx, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                if w < 30 or h < 20:  # Skip small elements
                    continue

                # Crop element and perform OCR
                cropped = image[y:y+h, x:x+w]
                text_results = reader.readtext(cropped, detail=0)
                element_text = ' '.join(text_results).strip() or f"Element-{idx+1}"
                ocr_texts.append(element_text)

                # Determine element type based on dimensions and text
                if w > 100 and h < 60 and any(word in element_text.lower() for word in ['button', 'btn', 'click']):
                    html = f'<button class="element-{idx}">{element_text}</button>'
                elif w > 100 and h < 40:
                    html = f'<input type="text" class="element-{idx}" placeholder="{element_text}">'
                else:
                    html = f'<div class="element-{idx}">{element_text}</div>'

                # Generate corresponding CSS
                css = f""".element-{idx} {{
                    position: absolute;
                    left: {x}px;
                    top: {y}px;
                    width: {w}px;
                    height: {h}px;
                    border: 1px solid #000;
                }}"""

                html_elements.append(html)
                css_elements.append(css)

            # Combine all generated code
            html_code = "<!-- Auto-generated HTML -->\n" + "\n".join(html_elements)
            css_code = "/* Auto-generated CSS */\n" + "\n".join(css_elements)
            js_code = "// Auto-generated JavaScript\nconsole.log('Page generated from image');"
            ocr_text = "\n".join(ocr_texts)

            # Create history record
            upload = UploadHistory.objects.create(
                user=request.user,
                cloud_image_url=cloud_url,
                framework_type=framework,
                css_style=css_type,
                html_code=html_code,
                css_code=css_code,
                js_code=js_code,
                ocr_text=ocr_text
            )

            # Clean up temp file
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")

            # Redirect to result page
            return redirect('result_page', upload_id=upload.id)

        except Exception as e:
            print(f"Error processing image: {e}")
            messages.error(request, f"Error processing image: {str(e)}")
            return redirect('dashboard')

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