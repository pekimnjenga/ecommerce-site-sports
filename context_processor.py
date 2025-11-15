from app.models import ItemCategory, Items


def category_context(request):
    categories = ItemCategory.objects.all()
    category_images = {}

    for category in categories:
        first_item = (
            Items.objects.filter(category=category).prefetch_related("images").first()
        )
        if first_item and first_item.images.exists():
            category_images[category.id] = first_item.images.first().image_url
        else:
            category_images[category.id] = (
                "app_templates/images/default.png"  # fallback
            )

    return {"categories": categories, "category_images": category_images}
