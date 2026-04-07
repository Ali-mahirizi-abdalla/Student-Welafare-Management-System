from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a value from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def is_eq(value, arg):
    """
    Template filter to compare if two values are equal.
    Usage: {{ value|is_eq:arg }}
    """
    return value == arg

@register.filter
def replace(value, arg):
    """
    Template filter to replace characters in a string.
    Usage: {{ value|replace:"old,new" }} or custom implementation.
    Django typically doesn't support multiple arguments for filters easily.
    I'll implement it to take a string like "_, " and split it.
    """
    if not isinstance(value, str):
        return value
    
    # Check if arg contains a comma to separate old and new
    if "," in arg:
        old, new = arg.split(",", 1)
        return value.replace(old, new)
    return value
