from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

import app.views as user_views

from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("signup/", user_views.sign_up, name="store-signup"),
    path("home/", user_views.home, name="store-home"),
    path(
        "login/",
        CustomLoginView.as_view(template_name="app_templates/login.html"),
        name="login",
    ),
    path(
        "logout/",
        CustomLogoutView.as_view(template_name="app_templates/logout.html"),
        name="logout",
    ),
    path("profile/", user_views.profile, name="profile"),
    path("my_orders/", user_views.orders, name="my_orders"),
    path(
        "category/<int:category_id>/", user_views.category_items, name="category_items"
    ),
]


# Configuring media files and static files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
