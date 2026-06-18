from django.shortcuts import render, redirect
from django.contrib import messages
from homeapp.models import tbl_user,tbl_company
from LCompany.models import tbl_ship,tbl_company_ship_route
from .forms import TransportationRequestForm,AddressForm,UserProfileForm,ReviewForm
from .models import tbl_transportation_request,tbl_payment,tbl_address,tbl_review
from django.utils import timezone
today = timezone.now().date()

def user_dashboard(request):

    if not request.session.get("login_id"):
        messages.error(request, "Please login first")
        return redirect("login")

    if request.session.get("usertype") != "user":
        messages.error(request, "Access denied")
        return redirect("login")

    try:
        user = tbl_user.objects.get(login_id=request.session["login_id"])
    except tbl_user.DoesNotExist:
        messages.error(request, "User profile not found")
        return redirect("login")

    # ✅ Address check
    address_exists = tbl_address.objects.filter(user_id=user).exists()

    # ✅ Recent transportation requests
    recent_requests = tbl_transportation_request.objects.select_related(
        "route_id"
    ).filter(
        user_id=user
    ).order_by("-requested_at")[:5]

    # ✅ Paid request IDs
    paid_request_ids = set(
        tbl_payment.objects.values_list("request_id_id", flat=True)
    )

    # ✅ Recent payments = activity log
    recent_payments = tbl_payment.objects.select_related(
        "request_id"
    ).filter(
        request_id__user_id=user
    ).order_by("-date")[:5]

    context = {
        "user_name": user.name,
        "user_email": user.login_id.email,
        "address_missing": not address_exists,
        "recent_requests": recent_requests,
        "recent_payments": recent_payments,
        "paid_request_ids": paid_request_ids,
        "active_page": "dashboard"
    }

    return render(request, "User_dashboard.html", context)


def search_ships(request):
    if request.session.get("usertype") != "user":
        return redirect("login")

    # Fetch all ships
    ships = tbl_ship.objects.all()

    # Fetch scheduled ships with related ship & company
    schedules = tbl_company_ship_route.objects.select_related(
        'ship_id'
    )

    context = {
        "ships": ships,
        "schedules": schedules
    }
    return render(request, "User_search_ships.html", context)

def send_transportation_request(request, ship_route_id):

    if request.session.get("usertype") != "user":
        return redirect("login")

    # Get user
    try:
        user = tbl_user.objects.get(
            login_id=request.session.get("login_id")
        )
    except:
        return redirect("login")

    # Get route
    try:
        ship_route = tbl_company_ship_route.objects.get(
            ship_route_id=ship_route_id
        )
    except:
        messages.error(request, "Route not found")
        return redirect("LUser:search_ships")

    ship = ship_route.ship_id
    company = ship.company_id
    route = ship_route.route_id

    if request.method == "POST":
        form = TransportationRequestForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user_id = user
            data.ship_id = ship
            data.company_id = company
            data.route_id = route
            data.status = "Pending"
            data.amount = "NULL"
            data.save()

            messages.success(request, "Request sent successfully")
            return redirect("LUser:user_dashboard")

    else:
        form = TransportationRequestForm()

    context = {
        "form": form,
        "ship": ship,
        "company": company,
        "route": route
    }

    return render(
        request,
        "User_send_request.html",
        context
    )
def view_ship_routes(request, ship_id):

    # 1. Check user type
    if request.session.get("usertype") != "user":
        messages.error(request, "Access denied")
        return redirect("login")

    # 2. Get ship
    try:
        ship = tbl_ship.objects.get(ship_id=ship_id)
    except:
        messages.error(request, "Ship not found")
        return redirect("LUser:search_ships")

    # 3. Get routes assigned to this ship
    routes = tbl_company_ship_route.objects.filter(
    ship_id=ship,
    status="Active",
    start_date__gte=today 
    )

    # 4. Context
    context = {
        "ship": ship,
        "company": ship.company_id,
        "routes": routes,
        "active_page": "search"
    }

    # 5. Render page
    return render(
        request,
        "User_view_ship_routes.html",
        context
    )
    
def user_view_requests(request):

    try:
        user = tbl_user.objects.get(
            login_id=request.session["login_id"]
        )
    except tbl_user.DoesNotExist:
        messages.error(request, "User not found")
        return redirect("login")

    requests = tbl_transportation_request.objects.select_related(
        'ship_id',
        'company_id',
        'route_id'
    ).filter(
        user_id=user
    ).order_by('-requested_at')

    # ✅ get all paid request ids
    paid_request_ids = set(
        tbl_payment.objects.values_list("request_id_id", flat=True)
    )

    return render(request, 'User_view_requests.html', {
        'requests': requests,
        'paid_request_ids': paid_request_ids,
        'active_page': 'sent_requests'
    })



def pay_shipping_fee(request, request_id):
    r = tbl_transportation_request.objects.get(request_id=request_id)

    return render(
        request,
        "User_pay_amount.html",
        {
            "r": r
        }
    )

def payment_success(request, request_id):

    if request.session.get("usertype") != "user":
        return redirect("login")

    r = tbl_transportation_request.objects.select_related(
        'ship_id',
        'company_id',
        'route_id',
        'user_id'
    ).get(request_id=request_id)

    # ✅ Prevent duplicate payment entries
    payment = tbl_payment.objects.filter(request_id=r).first()

    if not payment:
        payment = tbl_payment.objects.create(
            request_id=r,
            amount=r.amount,
            date=timezone.now()
        )

    context = {
        "r": r,
        "payment": payment,
        "invoice_no": f"INV-{payment.payment_id}",
        "paid_date": payment.date
    }

    return render(
        request,
        "User_payment_success.html",
        context
    )
def user_add_address(request):

    if not request.session.get("login_id"):
        return redirect("login")

    user = tbl_user.objects.get(
        login_id=request.session["login_id"]
    )

    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            addr = form.save(commit=False)

            # ✅ AUTO SET USER
            addr.user_id = user

            addr.save()

            messages.success(request, "Address saved successfully")
            return redirect("LUser:user_dashboard")

    else:
        form = AddressForm()

    return render(
        request,
        "User_add_address.html",
        {"form": form}
    )

def edit_user_profile(request):

    if request.session.get("usertype") != "user":
        return redirect("login")

    user = tbl_user.objects.get(
        login_id=request.session["login_id"]
    )

    address = tbl_address.objects.filter(user_id=user).first()

    if request.method == "POST":
        profile_form = UserProfileForm(
            request.POST,
            instance=user
        )

        address_form = AddressForm(
            request.POST,
            instance=address
        )

        if profile_form.is_valid() and address_form.is_valid():
            profile_form.save()

            addr = address_form.save(commit=False)
            addr.user_id = user
            addr.save()

            messages.success(request, "Profile updated successfully ✅")
            return redirect("LUser:user_dashboard")

    else:
        profile_form = UserProfileForm(instance=user)
        address_form = AddressForm(instance=address)

    return render(
        request,
        "User_edit_profile.html",
        {
            "profile_form": profile_form,
            "address_form": address_form,
            "active_page": "profile"
        }
    )
def view_available_routes(request):

    # ✅ login check
    if not request.session.get("login_id"):
        return redirect("login")

    if request.session.get("usertype") != "user":
        return redirect("login")

    # ✅ fetch all valid routes
    routes = tbl_company_ship_route.objects.select_related(
        "ship_id",
        "route_id",
        "ship_id__company_id"
    ).filter(
        status="Active",
        start_date__gte=today,
        arrival_date__gte=today
        # avoid expired ones
    ).order_by("start_date")

    context = {
        "routes": routes,
        "active_page": "routes"
    }

    return render(
        request,
        "User_available_routes.html",
        context
    )    
    
def completed_orders(request):

    if request.session.get("usertype") != "user":
        return redirect("login")

    user = tbl_user.objects.get(
        login_id=request.session["login_id"]
    )

    # ✅ completed + paid requests
    completed_requests = tbl_transportation_request.objects.select_related(
        "ship_id",
        "company_id",
        "route_id"
    ).filter(
        user_id=user,
        status="Completed"
    )

    paid_ids = set(
        tbl_payment.objects.values_list("request_id_id", flat=True)
    )

    completed_requests = completed_requests.filter(
        request_id__in=paid_ids
    )

    # ✅ existing reviews
    reviewed_ids = set(
        tbl_review.objects.filter(user_id=user)
        .values_list("request_id_id", flat=True)
    )

    context = {
        "orders": completed_requests,
        "reviewed_ids": reviewed_ids,
        "active_page": "completed"
    }

    return render(
        request,
        "User_completed_orders.html",
        context
    )    
    
def submit_review(request, request_id):

    if request.session.get("usertype") != "user":
        return redirect("login")

    user = tbl_user.objects.get(
        login_id=request.session["login_id"]
    )

    req = tbl_transportation_request.objects.get(
        request_id=request_id,
        user_id=user
    )

    # prevent duplicate review
    if tbl_review.objects.filter(
        request_id=req,
        user_id=user
    ).exists():
        messages.warning(request, "You already reviewed this order")
        return redirect("LUser:completed_orders")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user_id = user
            review.request_id = req
            review.save()

            messages.success(request, "Review submitted successfully ⭐")
            return redirect("LUser:completed_orders")

    else:
        form = ReviewForm()

    return render(
        request,
        "User_review_form.html",
        {
            "form": form,
            "req": req
        }
    )
    