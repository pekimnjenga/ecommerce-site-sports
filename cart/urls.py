from django.urls import path

import cart.views as user_views

urlpatterns = [
    path("mycart/", user_views.cart, name="mycart"),
    path("cart/add/<int:item_id>/", user_views.add_to_cart, name="add_to_cart"),
    path(
        "cart/remove/<int:item_id>/",
        user_views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("save-cart-intent/", user_views.save_cart_intent, name="save_cart_intent"),
    path(
        "process_cart_intent/",
        user_views.process_cart_intent,
        name="process_cart_intent",
    ),
    path("payment/pending/", user_views.payment_pending, name="payment_pending"),
]
