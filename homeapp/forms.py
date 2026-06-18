# forms.py
from django import forms
from .models import tbl_login, tbl_user, tbl_company
from django.core.exceptions import ValidationError
import re

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    phno = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    country = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    id_proof = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions'}
    )
    

    class Meta:
        model = tbl_user
        fields = ['name', 'phno', 'id_proof', 'country']
        

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and tbl_login.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different email.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and not re.match("^[A-Za-z ]+$", name):
            raise forms.ValidationError("Name should contain only alphabets and spaces.")
        return name

    def clean_phno(self):
        phno = self.cleaned_data.get("phno")
        if phno and not re.match("^[0-9]{10}$", phno):
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phno

    def clean_terms(self):
        terms = self.cleaned_data.get("terms")
        if not terms:
            raise forms.ValidationError("You must agree to the terms and conditions.")
        return terms   
   


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control fs-6 py-3 px-4 form-control-lg',
            'placeholder': 'Your Email',
            'required': 'required'
        }),
        label="Email"
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control fs-6 py-3 px-4 form-control-lg',
            'placeholder': 'Your Password',
            'required': 'required'
        }),
        label="Password"
    )
    
class CompanyRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    country = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    district = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    state = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    owner_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    id_proof = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    licence = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png',
            'id': 'id_licence'
        }),
        label="Business Licence Document"
    )

   
    
    
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the terms and conditions'}
    )    
    
    class Meta:
        model = tbl_company           
        fields = [
            'name',
            'country',
            'district',
            'state',
            'owner_name',
            # DO NOT include 'licence' here
        ]