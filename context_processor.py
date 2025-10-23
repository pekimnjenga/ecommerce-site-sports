from app.models import ItemCategory, Items


def category_context(request):
    categories = ItemCategory.objects.all()
    category_images = {}

    for category in categories:
        first_item = Items.objects.filter(category=category).first()
        if first_item and first_item.image:
            category_images[category.id] = first_item.image.url

    return {"categories": categories, "category_images": category_images}
