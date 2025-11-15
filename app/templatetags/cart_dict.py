from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def split_by_comma(value):
    if value:
        return [s.strip() for s in value.split(",")]
    return []


@register.filter
def cart_has(cart, key):
    return cart.get(key)
