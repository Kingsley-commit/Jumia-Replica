from django import template

register = template.Library()

@register.filter()
def subtract(value, subtract_from):
    return subtract_from - int(value)


@register.filter()
def discountprice(value, discount_percent):
    shaved_off_value = value * discount_percent/100 
    return value - shaved_off_value

@register.filter()
def discountpricesavings(value, discount_percent):
    return value * discount_percent/100 
    
