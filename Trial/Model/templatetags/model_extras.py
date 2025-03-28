from django import template

register = template.Library()

@register.filter
def get_dict_item(dictionary, key):
    """Template filter to access dictionary items by key."""
    if dictionary is None:
        return ''
    return dictionary.get(key, '')