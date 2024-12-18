from django.core.exceptions import ValidationError
from django.contrib.auth.models import User 

def validate_unique_username(value):
    if User.objects.filter(username=value).exists():
        raise ValidationError('This username already exist')
    
def validate_unique_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('This email is already registered.')
