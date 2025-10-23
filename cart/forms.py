from django import forms

from app.models import Order


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["phone_number", "address"]
        widgets = {
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your phone number (e.g., 0712345678)",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your delivery address",
                }
            ),
        }
