import easyocr
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone
from bifrost.models import ConversionRequest

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
    return render(request, 'frontend/history.html')

def result(request):
    return render(request, 'frontend/result.html')

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
