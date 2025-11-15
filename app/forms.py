from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

from .models import Items


# allow multiple file selection in admin form and return list of files
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if name in files:
            return files.getlist(name)
        return super().value_from_datadict(data, files, name)


# accept list of files during validation
class MultiFileField(forms.FileField):
    def clean(self, data, initial=None):
        # when widget returned a list of files, accept it as valid (return list)
        if isinstance(data, list):
            # filter out empty entries (if any)
            return [f for f in data if f is not None and getattr(f, "size", 0) > 0]
        return super().clean(data, initial)


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
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ["username", "email", "password"]


# Admin form for Items with multiple image uploads and size normalization
class ItemAdminForm(forms.ModelForm):
    # use MultiFileField so validation accepts lists
    images = MultiFileField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),
        help_text="Upload one or more images",
    )
    sizes = forms.CharField(required=False, help_text="Enter sizes like: S,M,L,XL")

    class Meta:
        model = Items
        fields = ["name", "category", "price", "stock", "description", "sizes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = getattr(self, "instance", None)
        imgs_qs = (
            getattr(inst, "images", None)
            if inst and getattr(inst, "pk", None)
            else None
        )
        if imgs_qs is not None:
            try:
                qs = imgs_qs.all()
            except Exception:
                qs = None
            if qs and qs.exists():
                previews = "".join(
                    f'<img src="{img.image_url}" width="100" height="100" style="margin:5px;" />'
                    for img in qs
                )
                self.fields["images"].help_text += mark_safe(
                    "<br><strong>Current Images:</strong><br>" + previews
                )
