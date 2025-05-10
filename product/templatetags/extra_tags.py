from django import template
from ..models import CartItem, UserCart

register = template.Library()

@register.filter()
def isproductincart(product_id, ids):
    for _list in ids:
        if product_id == _list[0]:
            return True
    return False

@register.filter()
def product_quantity(product_id, ids):
    for _list in ids:
        if product_id == _list[0]:
            return _list[1]
    return 1
