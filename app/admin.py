import os
import uuid

from django.contrib import admin

from app.supabase_utils import upload_image_to_supabase

from .forms import ItemAdminForm
from .models import ItemCategory, ItemImage, Items, Order


@admin.register(Items)
class ItemAdmin(admin.ModelAdmin):
    form = ItemAdminForm
    # remove image inline so admin shows only the images FileField on the form
    list_display = ["name", "category", "price", "stock"]

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        # ensure admin form renders as multipart (file uploads)
        context = context or {}
        context.setdefault("has_file_field", True)
        return super().render_change_form(request, context, add, change, form_url, obj)

    def save_model(self, request, obj, form, change):
        # proceed with save (keep original behavior)
        super().save_model(request, obj, form, change)
        files = request.FILES.getlist("images")
        for f in files:
            try:
                filename = f"{uuid.uuid4().hex}_{os.path.basename(f.name)}"
                # upload to supabase; your util should return the public URL
                public_url = upload_image_to_supabase(f, filename)
                ItemImage.objects.create(item=obj, image_url=public_url)
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to save/upload image {getattr(f, 'name', '<file>')}: {e}",
                    level="error",
                )


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    pass


admin.site.register(Order)
