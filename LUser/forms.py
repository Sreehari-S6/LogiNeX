from django import forms
from LUser.models import tbl_transportation_request,tbl_address,tbl_review
from django.contrib.auth.hashers import make_password, check_password
from homeapp.models import tbl_user

class TransportationRequestForm(forms.ModelForm):
    class Meta:
        model = tbl_transportation_request
        fields = [
            "container_type",
            "weight_ton",
            "pickup_address",
            "delivery_address",
        ]
        widgets = {
            "container_type": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Eg: 20ft Dry Container"
                }
            ),
            "weight_ton": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Weight in Tons"
                }
            ),
            "pickup_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Pickup address"
                }
            ),
            "delivery_address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Delivery address"
                }
            ),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = tbl_address
        exclude = ["user_id"]
        widgets = {
            "type": forms.Select(attrs={
                "class": "form-control", 
                "placeholder": "Select Type"
            }),
            "place": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "House/Flat No"
            }),
            "city": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "City"
            }),
            "district": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "District"
            }),
            "state": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "State"
            }),
            "pincode": forms.TextInput(attrs={
                "class": "form-control", 
                "placeholder": "Pincode"
            }),
        }


class UserProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        required=True,  # Made required so user must verify to save profile changes
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your current password"
        }),
        label="Current Password"
    )

    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Enter new password"
        }),
        label="New Password"
    )

    confirm_new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password"
        }),
        label="Confirm New Password"
    )

    class Meta:
        model = tbl_user
        fields = ["name", "phno"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phno": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        current_pass = cleaned_data.get("current_password")
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_new_password")

        # 1. Check if instance exists (it should in edit view)
        if self.instance and self.instance.login_id:
            # 2. Validate Current Password
            if not check_password(current_pass, self.instance.login_id.password):
                self.add_error('current_password', 'Current password is incorrect.')

        # 3. Validate New Password Match
        if new_pass and new_pass != confirm_pass:
            self.add_error('confirm_new_password', 'New passwords do not match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pass = self.cleaned_data.get("new_password")

        # Only update password if a new one was provided and validation passed
        if new_pass:
            user.login_id.password = make_password(new_pass)
            user.login_id.save()

        if commit:
            user.save()

        return user
    
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = tbl_review
        fields = ["comment"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your experience with this company..."
            })
        }
        labels = {
            "comment": "Your Review"
        }    