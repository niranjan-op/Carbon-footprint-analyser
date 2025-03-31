from django import template

register = template.Library()

@register.filter
def get_dict_item(dictionary, key):
    """Get an item from a dictionary, trying both the key as-is and as a string"""
    # For debugging
    print(f"Looking up key '{key}' (type: {type(key)}) in dictionary: {dictionary}")
    
    # Handle None or empty dictionary
    if not dictionary:
        print("Dictionary is empty or None")
        return '0'
    
    # Try the key as provided
    value = dictionary.get(key)
    if value is not None:
        print(f"Found value using original key: {value}")
        return value
    
    # Try the key as a string
    str_key = str(key)
    value = dictionary.get(str_key)
    if value is not None:
        print(f"Found value using string key: {value}")
        return value
    
    # If we get here, the key was not found in any format
    print(f"Key not found in dictionary")
    return '0'
