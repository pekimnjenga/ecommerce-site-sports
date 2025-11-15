import uuid

from django.contrib.auth.models import User
from django.db import models


class ItemCategory(models.Model):
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category


class Items(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.CASCADE,
        related_name="items",
        null=True,
        blank=True,
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(default="", blank=True)
    stock = models.IntegerField(default=0)
    sizes = models.CharField(
        max_length=100, blank=True, help_text="Comma-separated sizes like M,L,XL"
    )

    def add_stock(self, amount):
        self.stock += amount
        self.save()

    def subtract_stock(self, amount):
        if self.stock >= amount:
            self.stock -= amount
            self.save()
        else:
            raise ValueError("Insufficient stock")

    def delete(self, *args, **kwargs):
        from app.supabase_utils import delete_image_from_supabase

        for image in self.images.all():
            delete_image_from_supabase(image.image_url)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Item: {self.name} | Stock: {self.stock}"


class ItemImage(models.Model):
    item = models.ForeignKey(Items, related_name="images", on_delete=models.CASCADE)
    image_url = models.URLField()


class Order(models.Model):
    order_id = models.UUIDField(
        default=uuid.uuid4, unique=True, null=False, blank=False
    )
    reference_code = models.CharField(max_length=20, unique=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_time = models.TimeField(blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.order_id}"

    def save(self, *args, **kwargs):
        if not self.reference_code:
            self.reference_code = f"ORD{uuid.uuid4().hex[:10]}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.item.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} (Order {self.order.order_id})"
