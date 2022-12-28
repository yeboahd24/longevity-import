from django.shortcuts import render

from authapp.forms import DoctorSignInForm, DoctorSignUpForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic.base import TemplateView
from smtplib import SMTPDataError
from authapp.models import Doctor


class MainTemplateView(TemplateView):
    template_name = 'authapp/index.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['title'] = 'main'
        return context_data


def verify(request, email, activation_key):
    """Perform user verification."""

    try:
        user = Doctor.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print('activation was successful')
        else:
            print(f'user activation error: {email}')
        return render(request, "authapp/verification.html")
    except Exception as e:
        print(f'user activation error: {e.args}')
        return HttpResponseRedirect(reverse('authapp:main'))


def send_verify_email(user):
    """Send an email for user verification."""

    verify_link = reverse('authapp:verify', args=[user.email, user.activation_key])
    subject = f'user activation {user.username}'
    message = f'to confirm, follow the link: {settings.DOMAIN_NAME}{verify_link}'
    try:
        return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    except SMTPDataError:
        pass


def sign_in(request):
    title = "sign in"
    next_url = request.GET.get('next', '')
    login_form = DoctorSignInForm(data=request.POST)
    if request.method == 'POST' and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('authapp:main'))
    from_register = request.session.get('register', None)
    conf_code = request.session.get('conf_code', None)
    email = request.session.get('email', None)
    if from_register:
        del request.session['register']
        del request.session['conf_code']
        del request.session['email']

    content = {
        'title': title,
        'login_form': login_form,
        'next': next_url,
        'from_register': from_register,
        'confirmation': conf_code,
        'pth': f'{settings.DOMAIN_NAME}{request.get_full_path()}{email}{conf_code}',
        'email': email
    }
    return render(request, 'authapp/sign_in.html', content)


def sign_up(request):
    title = 'sign up'

    if request.method == 'POST':
        register_form = DoctorSignUpForm(request.POST, request.FILES)

        if register_form.is_valid():
            user = register_form.save()
            if send_verify_email(user):
                print('confirmation message sent')
                request.session['register'] = True
                user_name = request.POST['username']
                conf_code, email = [Doctor.objects.get(username=user_name).activation_key,
                                    Doctor.objects.get(username=user_name).email]
                request.session['conf_code'] = conf_code
                request.session['email'] = email

            else:
                print('error sending the message')
            return HttpResponseRedirect(reverse('authapp:sign_in'))

    else:
        register_form = DoctorSignUpForm()
    content = {
        'title': title,
        'register_form': register_form,
    }
    return render(request, 'authapp/sign_up.html', content)


def sign_out(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('authapp:main'))
