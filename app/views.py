from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localtime

from app.forms import UserModelForm
from app.models import ItemCategory, Order


def sign_up(request):
    if request.method == "POST":
        form = UserModelForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request, f"{username}, your account has been created successfully!"
            )
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            return redirect("store-signup")
    else:
        form = UserModelForm()  # ← This ensures 'form' is defined for GET requests

    context = {"form": form}
    return render(request, "app_templates/signup.html", context)


# Logging in users
class CustomLoginView(LoginView):
    template_name = "app_templates/login.html"
    redirect_authenticated_user = True  # Redirects authenitcated users to the homepage

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        # Getting the user object to retrieve the email
        user = User.objects.get(username=username)
        email = user.email if user.email else None

        # Store the username and email in the session
        self.request.session["user_email"] = email
        self.request.session["username"] = username
        # Flashing a welcome message in the default LoginView
        messages.success(self.request, f"Welcome back, {username}!")
        response.set_cookie(
            "sessionid", self.request.session.session_key, max_age=86400
        )
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def home(request):
    categories = ItemCategory.objects.all()
    category_images = {}
    for category in categories:
        first_item = category.items.first()
        category_images[category.id] = (
            first_item.image.url if first_item else "images/default.jpg"
        )
    context = {"categories": categories, "category_images": category_images}
    return render(request, "app_templates/home.html", context)


def category_items(request, category_id):
    cart = request.session.get("cart", {})
    category = get_object_or_404(ItemCategory, id=category_id)
    items = category.items.all()

    return render(
        request,
        "app_templates/category_items.html",
        {"items": items, "category": category, "cart": cart},
    )


# Users Profile
@login_required
def profile(request):
    user = request.user
    context = {"username": user.username, "email": user.email}
    return render(request, "app_templates/profile.html", context)


# View for viewing orders
@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user, is_paid=True).prefetch_related(
        "items__item"
    )
    order_dict = []

    for order in orders:
        items_summary = [
            {
                "name": item.item.name,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
            }
            for item in order.items.all()
        ]

        order_dict.append(
            {
                "order_id": order.order_id,
                "order_status": "Delivered" if order.is_delivered else "Pending",
                "delivery_time": (
                    localtime(order.delivery_time).strftime("%I:%M %p")
                    if order.is_delivered and order.delivery_time
                    else None
                ),
                "items": items_summary,
            }
        )

    message = "You currently have no orders" if not order_dict else ""
    return render(
        request,
        "app_templates/orders.html",
        {"order_dict": order_dict, "message": message},
    )


class CustomLogoutView(LogoutView):
    next_page = "store-home"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.success(
            request, "You have been successfully logged out. See you next time!"
        )
        response.delete_cookie("sessionid")  # Optional: clear session cookie
        return response
