from django.contrib import admin

from app.models import ItemCategory, Items, Order


# Defining how related objects (Items) are displayed in the admin interface and edited inline
class ItemInline(admin.TabularInline):
    model = Items
    extra = 0  # No extra blank forms


class ItemCategoryAdmin(admin.ModelAdmin):
    inlines = [ItemInline]  # Display items in the category


# Register your models here.
admin.site.register(Items)
admin.site.register(Order)
admin.site.register(ItemCategory)
