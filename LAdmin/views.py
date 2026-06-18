from pyexpat.errors import messages
from django.shortcuts import render, redirect
from homeapp.models import tbl_login, tbl_user, tbl_company
from LAdmin.models import tbl_routes
from LCompany.models import tbl_ship
from datetime import datetime
from LUser.models import tbl_payment   
from django.db.models import Count
from LUser.models import tbl_review
from LCompany.models import tbl_feedbacks



def admin_dashboard(request):

    if request.session.get("usertype") != "admin":
        return redirect("login")

    # -------- COUNTS --------
    total_users = tbl_user.objects.count()
    total_companies = tbl_company.objects.count()
    pending_companies = tbl_company.objects.filter(status="Pending").count()
    approved_companies = tbl_company.objects.filter(status="Approved").count()

    total_ships = tbl_ship.objects.count()
    total_routes = tbl_routes.objects.count()
    total_payments = tbl_payment.objects.count()

    # -------- TABLE DATA --------
    pending_company_list = tbl_company.objects.filter(status="Pending")[:5]

    ships = tbl_ship.objects.select_related("company_id") \
        .order_by("-ship_id")[:5]

    # -------- PIE CHART --------
    company_status_labels = ["Pending", "Approved"]
    company_status_values = [pending_companies, approved_companies]

    # -------- BAR CHART --------
    route_stats = tbl_routes.objects.values("departure_port") \
        .annotate(total=Count("departure_port"))

    route_labels = [r["departure_port"] for r in route_stats]
    route_values = [r["total"] for r in route_stats]

    context = {
        "total_users": total_users,
        "pending_companies": pending_companies,
        "total_ships": total_ships,
        "total_routes": total_routes,

        "pending_company_list": pending_company_list,
        "ships": ships,

        "company_status_labels": company_status_labels,
        "company_status_values": company_status_values,
        "route_labels": route_labels,
        "route_values": route_values,
    }

    return render(request, "admin_index.html", context)



def view_users(request):
    # Get all users with their login information
    users = tbl_user.objects.select_related('login_id').all()
    
    # Prepare data for template
    user_data = []
    for user_obj in users:
        user_data.append({
            'name': user_obj.name,
            'phno': user_obj.phno,
            'id_proof': user_obj.id_proof,
            'country': user_obj.country,
            'status': user_obj.status,
            'email': user_obj.login_id.email if user_obj.login_id else 'N/A',
        })
    
    context = {
        'users': user_data,
        'total_users': users.count(),
    }
    return render(request, 'admin_view_users.html', context)
def view_companies(request):
    if request.session.get("usertype") != "admin":
        return redirect("login")

    companies = tbl_company.objects.select_related('login_id').all()

    company_data = []
    for c in companies:
        company_data.append({
            'id': c.id,
            'name': c.name,
            'owner_name': c.owner_name,
            'country': c.country,
            'district': c.district,
            'state': c.state,
            'licence': c.licence,
            'status': c.status,
        })

    context = {
        'companies': company_data,
        'total_companies': companies.count(),
    }

    return render(request, 'admin_view_companies.html', context)

def update_company_status(request):
    if request.method == "POST":
        company_id = request.POST.get("company_id")
        status = request.POST.get("status")

        company = tbl_company.objects.get(id=company_id)
        company.status = status
        company.save()

    return redirect('LAdmin:view_companies')

def manage_routes(request):
    if request.session.get("usertype") != "admin":
        return redirect("login")

    # ADD ROUTE
    if request.method == "POST":
        departure_port = request.POST.get("departure_port")
        arrival_port = request.POST.get("arrival_port")

        if departure_port and arrival_port:
            tbl_routes.objects.create(
                departure_port=departure_port,
                arrival_port=arrival_port
            )
            return redirect("LAdmin:manage_routes")

    # VIEW ROUTES
    routes = tbl_routes.objects.all()

    context = {
        "routes": routes,
        "total_routes": routes.count()
    }

    return render(request, "admin_manage_routes.html", context)
def admin_view_ships(request):
    """
    Admin view to see all ships across all companies
    """

    # 1. Admin login check
    if not request.session.get("login_id"):
        messages.error(request, "Please login first")
        return redirect("login")

    # 2. Admin role check
    if request.session.get("usertype") != "admin":
        messages.error(request, "Access denied. Admin only.")
        return redirect("login")

    # 3. Fetch all ships with company info
    ships = tbl_ship.objects.select_related("company_id").all()

    context = {
        "ships": ships,
        "total_ships": ships.count(),
        "active_page": "ships"
    }

    return render(request, "Admin_view_ships.html", context)

def admin_view_all_reviews(request):

    # Admin check
    if request.session.get("usertype") != "admin":
        return redirect("login")

    # User → Company reviews
    user_reviews = tbl_review.objects.select_related(
        "user_id",
        "request_id",
        "request_id__company_id",
        "request_id__route_id",
        "request_id__ship_id"
    ).order_by("-date")

    # Company → Admin feedback
    company_feedbacks = tbl_feedbacks.objects.all().order_by("-feedback_id")

    context = {
        "user_reviews": user_reviews,
        "company_feedbacks": company_feedbacks,
        "total_user_reviews": user_reviews.count(),
        "total_feedbacks": company_feedbacks.count(),
        "active_page": "reviews"
    }

    return render(
        request,
        "Admin_view_reviews.html",
        context
    )
