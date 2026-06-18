from PIL import Image
from io import BytesIO
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from homeapp.models import tbl_company
from .models import tbl_ship,tbl_company_ship_route
from django.views.decorators.csrf import csrf_exempt
from .forms import ShipForm,CompanyShipRouteForm,ShipmentStatusForm,FeedbackForm,CompanyProfileForm,CompanyPasswordChangeForm
from LAdmin.models import tbl_routes
from LUser.models import tbl_transportation_request

def Company_Dashboard(request):

    if not request.session.get('login_id'):
        messages.error(request, "Please login first")
        return redirect('login')

    if request.session.get('usertype') != 'company':
        messages.error(request, "Access denied. Company login required.")
        return redirect('login')

    company = tbl_company.objects.get(
        login_id=request.session['login_id']
    )

    if company.status != 'Approved':
        return redirect('LCompany:pending_approval')

    # ✅ REAL COUNTS
    active_ships = tbl_ship.objects.filter(
        company_id=company,
        status="Active"
    ).count()

    active_routes = tbl_company_ship_route.objects.filter(
        ship_id__company_id=company,
        status="Active"
    ).count()

    pending_requests = tbl_transportation_request.objects.filter(
        company_id=company,
        status="Pending"
    ).count()

    # ✅ Recent shipments (latest 5 requests)
    recent_shipments = tbl_transportation_request.objects.filter(
        company_id=company
    ).select_related("route_id").order_by("-requested_at")[:5]

    context = {
        "company": company,
        "company_name": company.name,
        "active_page": "dashboard",

        # dashboard stats
        "active_ships": active_ships,
        "active_routes": active_routes,
        "pending_requests": pending_requests,
        "recent_shipments": recent_shipments,
    }

    return render(request, "Company_Dashboard.html", context)
    
def manage_ships(request):
    if request.session.get("usertype") != "company":
        return redirect("login")

    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    ships = tbl_ship.objects.filter(company_id=company)

    return render(request, "Company_manage_ships.html", {
        "ships": ships
    })


def add_ship(request):
    if request.session.get("usertype") != "company":
        return redirect("login")

    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    if request.method == "POST":
        form = ShipForm(request.POST, request.FILES)
        if form.is_valid():
            ship = form.save(commit=False)
            ship.company_id = company   # 🔑 auto assign company
            ship.save()
            messages.success(request, "Ship added successfully")
            return redirect("LCompany:manage_ships")
    else:
        form = ShipForm()

    return render(request, "Company_add_ship.html", {
        "form": form
    })    
    

def add_ship_route(request):

    if request.session.get("usertype") != "company":
        return redirect("login")

    try:
        company = tbl_company.objects.get(
            login_id=request.session["login_id"]
        )
    except tbl_company.DoesNotExist:
        messages.error(request, "Company not found")
        return redirect("login")

    # ---- FORM ----
    if request.method == "POST":
        form = CompanyShipRouteForm(request.POST)
    else:
        form = CompanyShipRouteForm()

    # ---- FILTER DROPDOWNS ----
    form.fields['ship_id'].queryset = tbl_ship.objects.filter(
        company_id=company,
        status="Active"
    )
    form.fields['route_id'].queryset = tbl_routes.objects.all()

    # ---- SAVE ----
    if request.method == "POST" and form.is_valid():
        ship_route = form.save(commit=False)
        ship_route.status = "Active"
        ship_route.save()

        messages.success(request, "Ship route assigned successfully")
        return redirect("LCompany:add_ship_route")

    # ✅ ADD THIS PART HERE (THIS IS WHAT YOU ASKED)
    assigned_routes = tbl_company_ship_route.objects.filter(
        ship_id__company_id=company
    ).select_related('ship_id', 'route_id')

    # ---- FINAL RENDER ----
    return render(request, "Company_manage_shiproutes.html", {
        "form": form,
        "assigned_routes": assigned_routes,   # 👈 passed to template
        "active_page": "ship_routes"
    })
    
def view_requests(request):

    # 1. Check company login
    if not request.session.get("login_id"):
        messages.error(request, "Please login first")
        return redirect("login")

    if request.session.get("usertype") != "company":
        messages.error(request, "Access denied")
        return redirect("login")

    # 2. Get company (reuse session pattern)
    company_id = request.session.get("company_id")

    if not company_id:
        try:
            company = tbl_company.objects.get(
                login_id=request.session["login_id"]
            )
            company_id = company.id
            request.session["company_id"] = company_id
        except tbl_company.DoesNotExist:
            messages.error(request, "Company not found")
            return redirect("login")

    company = tbl_company.objects.get(id=company_id)

    # 3. Fetch shipping requests for this company
    requests = tbl_transportation_request.objects.filter(
        company_id=company
    ).select_related(
        "user_id",
        "ship_id",
        "route_id"
    ).order_by("-requested_at")

    # 4. Render page
    return render(request, "Company_view_requests.html", {
        "requests": requests,
        "active_page": "requests"
    })

def update_request_status(request, request_id):

    if request.session.get("usertype") != "company":
        return redirect("login")

    try:
        req = tbl_transportation_request.objects.get(
            request_id=request_id
        )
    except tbl_transportation_request.DoesNotExist:
        messages.error(request, "Request not found")
        return redirect("LCompany:view_requests")

    if request.method == "POST":
        status = request.POST.get("status")

        if status in ["Approved", "Rejected", "Under Consideration"]:
            req.status = status

            # 🔴 IMPORTANT: clear payment if rejected
            if status == "Rejected":
                req.amount = None

            req.save()
            messages.success(request, "Request status updated")

    return redirect("LCompany:view_requests")


def add_shipping_payment(request, request_id):

    if request.session.get("usertype") != "company":
        return redirect("login")

    try:
        req = tbl_transportation_request.objects.get(
            request_id=request_id
        )
    except tbl_transportation_request.DoesNotExist:
        messages.error(request, "Request not found")
        return redirect("LCompany:view_requests")

    # Only allow payment if Approved
    if req.status != "Approved":
        messages.warning(request, "Payment allowed only for approved requests")
        return redirect("LCompany:view_requests")

    if request.method == "POST":
        amount = request.POST.get("amount")

        if amount:
            req.amount = amount
            req.save()
            messages.success(request, "Shipping fee added successfully")

    return redirect("LCompany:view_requests")

from LUser.models import tbl_review

def company_reviews(request):

    if request.session.get("usertype") != "company":
        return redirect("login")

    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    reviews = tbl_review.objects.select_related(
        "user_id",
        "request_id",
        "request_id__route_id",
        "request_id__ship_id"
    ).filter(
        request_id__company_id=company
    ).order_by("-date")

    context = {
        "reviews": reviews,
        "active_page": "reviews"
    }

    return render(
        request,
        "Company_reviews.html",
        context
    )

def update_shipment_status_page(request):

    if request.session.get("usertype") != "company":
        return redirect("login")

    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    requests = tbl_transportation_request.objects.select_related(
        "user_id",
        "route_id",
        "ship_id"
    ).filter(
        company_id=company
    ).order_by("-requested_at")

    return render(
        request,
        "Company_update_shipment_status.html",
        {
            "requests": requests,
            "active_page": "shipment_status"
        }
    )
    
def update_shipment_status(request, request_id):

    if request.session.get("usertype") != "company":
        return redirect("login")

    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    req = tbl_transportation_request.objects.get(
        request_id=request_id,
        company_id=company
    )

    if request.method == "POST":
        form = ShipmentStatusForm(
            request.POST,
            instance=req
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Shipment status updated ✅")

    return redirect("LCompany:update_shipment_status_page")
    
def send_feedback(request):

    if request.session.get("usertype") != "company":
        return redirect("login")

    # optional: auto-fill from company profile
    company = tbl_company.objects.get(
        login_id=request.session["login_id"]
    )

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Feedback sent to admin ✅")
            return redirect("LCompany:send_feedback")

    else:
        # prefill
        form = FeedbackForm(initial={
            "name": company.name,
            "email": company.login_id.email
        })

    return render(
        request,
        "Company_send_feedback.html",
        {
            "form": form,
            "active_page": "feedback"
        }
    )        
    

def edit_company_profile(request):

    if request.session.get("usertype") != "company":
        return redirect("login")

    try:
        company = tbl_company.objects.get(
            login_id=request.session["login_id"]
        )
    except tbl_company.DoesNotExist:
        messages.error(request, "Company not found")
        return redirect("login")

    login_obj = company.login_id

    profile_form = CompanyProfileForm(instance=company)
    password_form = CompanyPasswordChangeForm()

    if request.method == "POST":

        # ================= PROFILE SAVE =================
        if "save_profile" in request.POST:

            profile_form = CompanyProfileForm(
                request.POST,
                request.FILES,
                instance=company
            )

            if profile_form.is_valid():

                obj = profile_form.save(commit=False)

                licence_file = request.FILES.get("licence")

                # ✅ Pillow image save → media/licences/
                if licence_file:
                    try:
                        img = Image.open(licence_file)
                        img = img.convert("RGB")
                        img.thumbnail((1400, 1400))

                        filename = f"licence_{int(time.time())}.jpg"
                        db_path = f"licences/{filename}"

                        buffer = BytesIO()
                        img.save(buffer, format="JPEG", quality=90)

                        saved_path = default_storage.save(
                            db_path,
                            ContentFile(buffer.getvalue())
                        )

                        obj.licence = saved_path

                    except Exception:
                        messages.error(
                            request,
                            "Invalid licence image ❌"
                        )
                        return redirect("LCompany:edit_company_profile")

                obj.save()
                messages.success(request, "Profile updated ✅")
                return redirect("LCompany:edit_company_profile")

        # ================= PASSWORD CHANGE =================
        if "change_password" in request.POST:

            password_form = CompanyPasswordChangeForm(request.POST)

            if password_form.is_valid():

                old_pw = password_form.cleaned_data["old_password"]
                new_pw = password_form.cleaned_data["new_password"]

                if login_obj.password != old_pw:
                    messages.error(
                        request,
                        "Old password incorrect ❌"
                    )
                else:
                    login_obj.password = new_pw
                    login_obj.save()

                    messages.success(
                        request,
                        "Password changed successfully ✅"
                    )

                    return redirect("LCompany:edit_company_profile")

    return render(
        request,
        "Company_edit_profile.html",
        {
            "profile_form": profile_form,
            "password_form": password_form,
            "company": company,
            "active_page": "profile"
        }
    )
