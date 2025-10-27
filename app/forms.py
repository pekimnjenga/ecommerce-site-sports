from django import forms
from django.contrib.auth.models import User


class UserModelForm(forms.ModelForm):
    username = forms.CharField(max_length=100, required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(max_length=150, required=True, label="Password")
    confirm_password = forms.CharField(
        max_length=150, required=True, label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("The passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "email", "password"]
