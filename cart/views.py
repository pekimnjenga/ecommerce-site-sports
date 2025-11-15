import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from app.models import Items, Order, OrderItem

from .forms import PaymentForm
from .stk_push import initiate_stk_push

logger = logging.getLogger(__name__)


@require_POST
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    cart = request.session.get("cart", {})

    # Get quantity and size
    quantity = int(request.POST.get("quantity", 1))
    size = request.POST.get("size")

    # Enforce size selection only if item requires it
    if item.sizes and not size:
        messages.warning(request, "Please select a size before adding to cart.")
        return redirect("item_details", item_id=item_id)

    # Save selected size to session
    if size:
        selected_sizes = request.session.get("selected_sizes", {})
        selected_sizes[str(item_id)] = size
        request.session["selected_sizes"] = selected_sizes

    # Build item key and update cart
    item_key = f"{item_id}:{size}" if size else str(item_id)
    cart[item_key] = quantity
    request.session["cart"] = cart

    return redirect("mycart")


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(Items.objects.prefetch_related("images"), id=item_id)
    cart = request.session.get("cart", {})
    stock = item.stock
    size = request.POST.get("size")
    item_key = f"{item_id}:{size}" if size else str(item_id)
    quantity = int(request.POST.get("quantity", 1))
    action = request.POST.get("action")

    if action == "increase" and quantity < stock:
        quantity += 1
        cart[item_key] = quantity
    elif action == "decrease" and quantity > 0:
        quantity -= 1
        cart[item_key] = quantity
    elif action == "decrease" and quantity == 0:
        cart[item_key] = 0
    elif action == "add":
        cart[item_key] = quantity
    elif action == "remove":
        cart.pop(item_key, None)
    if cart.get(item_key, 0) == 0:
        cart.pop(item_key, None)
    request.session["cart"] = cart
    return redirect(
        request.META.get("HTTP_REFERER", "category_items")
    )  # Redirecting the user to the same page


@login_required
def cart(request):
    cart = request.session.get("cart", {})
    logger.info("Cart session retrieved for user %s: %s", request.user.username, cart)

    cart_items = []
    total = 0

    for key, quantity in cart.items():
        if ":" in key:
            item_id, size = key.split(":", 1)
        else:
            item_id, size = key, None
        item = Items.objects.get(id=item_id)
        amount = item.price * quantity
        total += amount
        cart_items.append(
            {
                "item": item,
                "quantity": quantity,
                "amount": float(amount),
                "size": size,
            }
        )

    logger.info(
        "Cart items calculated for user %s: %s", request.user.username, cart_items
    )
    logger.info("Total amount for cart: %.2f", total)

    if request.method == "POST":
        form = PaymentForm(request.POST)
        logger.info("Payment form submitted by user %s", request.user.username)

        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            address = form.cleaned_data["address"]
            logger.info("Form validated. Phone: %s, Address: %s", phone_number, address)

            # Normalize phone number
            original_phone = phone_number
            if phone_number.startswith("0"):
                phone_number = "254" + phone_number[1:]
            elif phone_number.startswith("+254"):
                phone_number = phone_number[1:]
            elif not phone_number.startswith("254"):
                logger.warning(
                    "Unexpected phone format from user %s: %s",
                    request.user.username,
                    original_phone,
                )
                return render(
                    request,
                    "cart_templates/cart.html",
                    {
                        "cart_items": cart_items,
                        "total": float(total),
                        "form": form,
                        "cart": cart,
                        "error": "Invalid phone number format.",
                    },
                )
            logger.info(
                "Normalized phone number for user %s: %s",
                request.user.username,
                phone_number,
            )

            # Create order
            order = Order.objects.create(
                user=request.user,
                phone_number=phone_number,
                address=address,
                total_amount=total,
                is_paid=False,
                transaction_date=timezone.now(),
            )
            logger.info(
                "Order created: %s with reference_code %s",
                order.id,
                order.reference_code,
            )

            # Create order items
            for entry in cart_items:
                OrderItem.objects.create(
                    order=order,
                    item=entry["item"],
                    quantity=entry["quantity"],
                    subtotal=entry["amount"],
                    size=entry["size"],
                )
            logger.info("OrderItems created for Order %s", order.id)

            # Trigger STK Push
            account_reference = str(order.reference_code).replace("-", "")[:20]
            response = initiate_stk_push(
                phone_number=phone_number,
                amount=float(total),
                account_reference=account_reference,
                transaction_desc=f"Payment for {request.user.username}",
            )
            logger.info(
                "STK Push Payload for Order %s: %s",
                order.id,
                json.dumps(
                    {
                        "phone_number": phone_number,
                        "amount": float(total),
                        "account_reference": account_reference,
                        "transaction_desc": f"Payment for {request.user.username}",
                    },
                    indent=2,
                ),
            )
            logger.info("STK Push response for Order %s: %s", order.id, response)

            # Track pending order
            request.session["pending_order_id"] = order.id
            logger.info("Pending order ID stored in session: %s", order.id)

            # Optional: clear cart
            request.session["cart"] = {}
            logger.info("Cart cleared for user %s", request.user.username)

            return redirect("payment_pending")

        else:
            logger.warning(
                "Payment form invalid for user %s: %s",
                request.user.username,
                form.errors,
            )

    else:
        form = PaymentForm()
        logger.info("Cart page loaded for user %s", request.user.username)

    return render(
        request,
        "cart_templates/cart.html",
        {"cart_items": cart_items, "total": total, "form": form, "cart": cart},
    )


@login_required
def payment_pending(request):
    order_id = request.session.get("pending_order_id")
    if not order_id:
        return redirect("mycart")

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return redirect("mycart")

    if order.is_paid:
        return redirect("success_page")

    return render(request, "cart_templates/payment_pending.html", {"order": order})


@csrf_exempt
def save_cart_intent(request):
    login_url = reverse("login")
    next_url = reverse("process_cart_intent")
    if request.method == "POST":
        request.session["cart_intent"] = {
            "item_id": request.POST.get("item_id"),
            "quantity": request.POST.get("quantity"),
            "action": request.POST.get("action"),
            "return_to": request.POST.get("return_to", "/"),
        }
        return redirect(f"{login_url}?next={next_url}")
    return redirect("store-home")


@login_required
def process_cart_intent(request):
    intent = request.session.pop("cart_intent", None)
    if intent:
        item_id = intent.get("item_id")
        quantity = int(intent.get("quantity", 1))
        action = intent.get("action")
        return_to = intent.get("return_to", "/")
        cart = request.session.get("cart", {})
        size = request.session.get("selected_sizes", {}).get(str(item_id))
        item_key = f"{item_id}:{size}" if size else str(item_id)

        if action == "add":
            cart[item_key] = cart.get(item_key, 0) + quantity
        elif action == "increase":
            cart[item_key] = cart.get(item_key, 0) + 1
        elif action == "decrease":
            cart[item_key] = max(cart.get(item_key, 1) - 1, 0)
            if cart[item_key] == 0:
                cart.pop(item_key, None)

        request.session["cart"] = cart
        return redirect(return_to)

    return redirect("store-home")
