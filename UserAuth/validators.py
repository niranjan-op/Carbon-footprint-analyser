import re
from django.core.exceptions import ValidationError
def validate_password_strength(value):
    if len(value)<8:
        raise ValidationError("Password is too short. It should have at least 8 characters")
    if not re.search(r'\d',value):
        raise ValidationError("Password must contain at least one digit")
    if not re.search(r'[A-Z]',value):
        raise ValidationError("Password must contain at least one UpperCase character")
    if not re.search(r'[a-z]',value):
        raise ValidationError("Password must contain at least one LowerCase character")
    if not re.search(r'[@$#%^*!&(){}|<>?,.:;/\':~`=+_-]',value):
        raise ValidationError("Password must contain at least one special character")
    
def validate_username_strength(value):
    if(len(value)<5):
        raise ValidationError("Username is too short. Username should contain at least 5 characters.")
    if not re.search(r'[a-zA-Z0-9]+$',value):
        raise ValidationError("Username should contain only alphabets, numbers and underscores")
