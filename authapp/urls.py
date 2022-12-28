from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
import authapp.views as authapp

app_name = 'authapp'

urlpatterns = [
    path('', authapp.MainTemplateView.as_view(), name='main'),
    path('sign_in/', authapp.sign_in, name='sign_in'),
    path('sign_up/', authapp.sign_up, name='sign_up'),
    path('sign_out/', authapp.sign_out, name='sign_out'),
    path('verify/<email>/<activation_key>/', authapp.verify, name='verify'),
]