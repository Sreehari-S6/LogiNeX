from django.shortcuts import render
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm , CompanyRegistrationForm 
import os
import uuid                  # <-- Needed for uuid.uuid4()
from django.conf import settings  # <-- Needed for settings.MEDIA_ROOT
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
import traceback
from .models import tbl_login, tbl_otp


def loadindex(request):
    return render(request,'index.html')

from django.shortcuts import render, redirect

from .models import tbl_login, tbl_user, tbl_company

def register(request):
    """
    Handle user registration
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Step 1: Get cleaned data
                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]
                name = form.cleaned_data["name"]
                phno = form.cleaned_data["phno"]
                country = form.cleaned_data["country"]
                id_proof = form.cleaned_data["id_proof"]

                # Step 2: Create user in Login table
                login_user = tbl_login.objects.create(
                    email=email, 
                    password=password,
                    usertype='user'
                )

                # Step 3: Create user profile linked to login
                user = form.save(commit=False)
                user.login_id = login_user  # Link to login table
                user.save()

                # Step 4: Show success message and redirect to login page
                messages.success(request, "Registration successful! Please login to continue.")
                return redirect("login")
                
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
                print(f"Registration error: {e}")
        else:
            # Show form errors
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Invalid form data")
            return render(request, "login.html", {"form": form})

        email = form.cleaned_data["email"].strip()
        password = form.cleaned_data["password"].strip()

        print("LOGIN ATTEMPT:", email)

        try:
            # STEP 1: Check email exists
            try:
                user = tbl_login.objects.get(email=email)
            except tbl_login.DoesNotExist:
                print("EMAIL NOT FOUND")
                messages.error(request, "Email not registered")
                return render(request, "login.html", {"form": form})

            # STEP 2: Check password
            if user.password != password:
                print("WRONG PASSWORD")
                messages.error(request, "Incorrect password")
                return render(request, "login.html", {"form": form})

            # STEP 3: Success → set session
            request.session.clear()
            request.session["login_id"] = user.id
            request.session["email"] = user.email
            request.session["usertype"] = user.usertype

            print("LOGIN SUCCESS:", user.email, user.usertype)

            try:
                company = tbl_company.objects.get(login_id=user.id)
                request.session["company_id"] = company.id
                request.session["company_name"] = company.name
                request.session["company_status"] = company.status
                print(f"Company found: {company.name}, Status: {company.status}")
            except tbl_company.DoesNotExist:
                print("Company profile not found")

            # STEP 4: Redirect
            if user.usertype == "admin":
                return redirect("LAdmin:admin_dashboard")
            elif user.usertype == "user":
                return redirect("LUser:user_dashboard")
            elif user.usertype == "company":
                return redirect("LCompany:Company_Dashboard")

            messages.error(request, "Invalid user role")
            return render(request, "login.html", {"form": form})

        except Exception as e:
            print("=" * 60)
            print("LOGIN ERROR:", e)
            traceback.print_exc()
            print("=" * 60)
            raise

    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})
def logout(request):
    """
    Handle user logout
    """
    # Clear all session data
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# Optional: Dashboard view for authenticated users
def user_dashboard(request):
    """
    Display user dashboard
    """
   

    return render(request, "user_dashboard.html")

def company_register(request):
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Create login record
                login = tbl_login(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data["password"],
                    usertype='company'
                )
                login.save()
                
                licence_file = form.cleaned_data['licence']

                ext = os.path.splitext(licence_file.name)[1]
                filename = f"licence_{uuid.uuid4().hex}{ext}"

                upload_dir = os.path.join(settings.MEDIA_ROOT, 'licences')
                os.makedirs(upload_dir, exist_ok=True)

                file_path = os.path.join(upload_dir, filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in licence_file.chunks():
                        destination.write(chunk)

# store path or filename (choose ONE)
                licence_db_path = f"licences/{filename}"   # OR just filename

                company = tbl_company(
                 name=form.cleaned_data['name'],
                login_id=login,
                country=form.cleaned_data['country'],
                district=form.cleaned_data['district'],
                state=form.cleaned_data['state'],
                owner_name=form.cleaned_data['owner_name'],
                licence=licence_db_path,     # ✅ FIX HERE
                id_proof=form.cleaned_data['id_proof'],
                status='Pending'
                )
                company.save()

                messages.success(request, 'Company registration successful! Your account is pending admin approval.')
                # Redirect to login page or success page
                return redirect('login')
                
            except Exception as e:
                # Delete the login record if company creation fails
                
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'company_registration.html', {'form': form})
        else:
            # Form is invalid, show errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'company_registration.html', {'form': form})

def logout_view(request):
    """
    Global logout view
    - Clears all session data
    - Redirects to login page
    """

    # Clear entire session
    request.session.flush()

    # Optional user feedback
    messages.success(request, "Logged out successfully")

    return redirect("login")

def about(request):
    return render(request, "about.html")


def services(request):
    return render(request, "services.html")

def forgot_password(request):

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            login = tbl_login.objects.get(email=email)

            # generate otp
            otp = str(random.randint(100000, 999999))

            # store otp
            tbl_otp.objects.create(
                email=email,
                otp=otp,
                timestamp=timezone.now(),
                status='pending'
            )

            # send email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )

            request.session['reset_email'] = email
            return redirect("verify_otp")

        except tbl_login.DoesNotExist:
            return render(request, "forgot_password.html", {"error": "Email not registered"})

    return render(request, "forgot_password.html")

def verify_otp(request):

    if request.method == "POST":
        user_otp = request.POST.get("otp")
        email = request.session.get("reset_email")

        try:
            otp_obj = tbl_otp.objects.filter(
                email=email,
                otp=user_otp,
                status='pending'
            ).latest('timestamp')

            # check expiry (5 minutes)
            if timezone.now() - otp_obj.timestamp > timedelta(minutes=5):
                return render(request, "verify_otp.html", {"error": "OTP expired"})

            otp_obj.status = "used"
            otp_obj.save()

            return redirect("reset_password")

        except tbl_otp.DoesNotExist:
            return render(request, "verify_otp.html", {"error": "Invalid OTP"})

    return render(request, "verify_otp.html")

def reset_password(request):

    if request.method == "POST":
        p1 = request.POST.get("password")
        p2 = request.POST.get("confirm_password")

        if p1 != p2:
            return render(request, "reset_password.html", {"error": "Passwords not matching"})

        email = request.session.get("reset_email")

        login = tbl_login.objects.get(email=email)
        login.password = p1   # if hashed system exists, hash here
        login.save()

        return redirect("login")

    return render(request, "reset_password.html")
