from django import forms
from datetime import date
from .models import tbl_ship,tbl_company_ship_route,tbl_feedbacks
from LAdmin.models import tbl_routes
from LUser.models import tbl_transportation_request
from homeapp.models import tbl_company
class ShipForm(forms.ModelForm):
    class Meta:
        model = tbl_ship
        fields = ['ship_name', 'capacity_ton', 'built_year', 'image',]

    def clean_ship_name(self):
        ship_name = self.cleaned_data.get('ship_name')
        if len(ship_name) < 3:
            raise forms.ValidationError("Ship name must be at least 3 characters")
        return ship_name

    def clean_capacity_ton(self):
        capacity = self.cleaned_data.get('capacity_ton')
        if capacity <= 0:
            raise forms.ValidationError("Capacity must be greater than zero")
        return capacity

    def clean_built_year(self):
        year = self.cleaned_data.get('built_year')
        current_year = date.today().year
        if year < 1950 or year > current_year:
            raise forms.ValidationError(
                f"Built year must be between 1950 and {current_year}"
            )
        return year


class CompanyShipRouteForm(forms.ModelForm):
    class Meta:
        model = tbl_company_ship_route
        fields = ['ship_id', 'route_id', 'start_date', 'arrival_date']

        widgets = {
            'ship_id': forms.Select(attrs={'class': 'form-select'}),
            'route_id': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'arrival_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        arrival_date = cleaned_data.get("arrival_date")

        if start_date and arrival_date and arrival_date < start_date:
            raise forms.ValidationError(
                "Arrival date must be after start date."
            )

        return cleaned_data
STATUS_CHOICES = [
    ("Started", "Started"),
    ("On Transit", "On Transit"),
    ("completed", "completed"),
]

class ShipmentStatusForm(forms.ModelForm):

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = tbl_transportation_request
        fields = ["status"]
        
class FeedbackForm(forms.ModelForm):

    class Meta:
        model = tbl_feedbacks
        fields = ["name", "email", "contact_no", "message"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "contact_no": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5
            }),
        }      
        
class CompanyProfileForm(forms.ModelForm):

    class Meta:
        model = tbl_company
        fields = [
            "name",
            "owner_name",
            "country",
            "district",
            "state",
            "licence",
            "id_proof",
        ]
        
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "owner_name": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "licence": forms.TextInput(attrs={"class": "form-control"}),
            "id_proof": forms.TextInput(attrs={"class": "form-control"}),
              "licence": forms.FileInput()
        }          
        licence = forms.FileField(required=False)
        
from django import forms

class CompanyPasswordChangeForm(forms.Form):

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Old Password"
    )

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="New Password"
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Confirm Password"
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("new_password") != cleaned.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match")
        return cleaned
        