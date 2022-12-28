from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta


class Doctor(AbstractUser):

    MALE = 'М'
    FEMALE = 'W'

    GENDER_CHOICES = (
        (MALE, 'M'),
        (FEMALE, 'W')
    )

    SURGEON = 'SURGEON'
    ONCOLOGIST = 'ONCOLOGIST'
    THERAPIST = 'THERAPIST'

    PROFESION_CHOICES = (
        (None, 'Select your profession'),
        (SURGEON, 'Surgeon'),
        (ONCOLOGIST, 'Oncologist'),
        (THERAPIST, 'Therapist'),
    )

    avatar = models.ImageField(upload_to='users_avatars', blank=True)
    age = models.PositiveSmallIntegerField(default=18)
    email = models.EmailField(max_length=150, unique=True)
    profession = models.CharField(max_length=32, choices=PROFESION_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    activation_key = models.CharField(max_length=128, blank=True)
    activation_key_expires = models.DateTimeField(default=(now() + timedelta(hours=48)))

    class Meta:
        verbose_name = 'doctor'
        verbose_name_plural = 'doctors'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def is_activation_key_expired(self):
        if now() <= self.activation_key_expires:
            return False
        else:
            return True
