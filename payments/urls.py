from django.urls import path

from . import views

urlpatterns = [
    path("success/", views.success_page, name="success_page"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
]
