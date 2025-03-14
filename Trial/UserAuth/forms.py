from django import forms
from django.contrib.auth.models import User
from .validators import validate_password_strength, validate_username_strength

class SignupForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput,validators=[validate_password_strength])
    username=forms.CharField(validators=[validate_username_strength])
    class Meta:
        model = User
        fields = ['username','password']
    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user