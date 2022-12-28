from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Doctor
from django import forms
import hashlib
from random import random


class DoctorSignInForm(AuthenticationForm):

    class Meta:
        model = Doctor
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.help_text = ''
            field.error_messages['required'] = ''


class DoctorSignUpForm(UserCreationForm):
    class Meta:
        model = Doctor
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2',
                  'email', 'avatar', 'age', 'gender', 'profession')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.help_text = ''
            field.error_messages['required'] = ''

    def save(self, **kwargs):
        doctor = super().save()
        doctor.is_active = False
        salt = hashlib.sha1(str(random()).encode('utf8')).hexdigest()[:6]
        doctor.activation_key = hashlib.sha1((doctor.email + salt).encode('utf8')).hexdigest()
        doctor.save()

        return doctor
