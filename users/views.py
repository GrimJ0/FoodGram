from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import CreateView

from app.models import ShopList, User
from foodgram import settings

from .forms import CreationForm


class SignUp(CreateView):
    """
    Класс регистрации пользователя
    """
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.get('purchase_id')
        if session_key:
            context['purchases'] = ShopList.objects.filter(
                session_key=session_key
            ).select_related('recipe').values_list('recipe', flat=True)

        return context

    def form_valid(self, form):
        session_key = self.request.session.get('purchase_id')
        user = form.save(commit=False)
        user.save()
        if session_key:
            shop_list = ShopList.objects.select_related('recipe').filter(session_key=session_key)
            user.users.add(*shop_list)
        return super().form_valid(form)


class LoginUser(LoginView):
    """
    Класс авторизации пользователя
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.get('purchase_id')
        if session_key:
            context['purchases'] = ShopList.objects.filter(
                session_key=session_key
            ).select_related('recipe').values_list('recipe', flat=True)

        return context


def password_reset_request(request):
    """
        Функция для отправки формы на email пользователя для сброса пароля
    """
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            mail = password_reset_form.cleaned_data['email']
            try:
                user = User.objects.get(email=mail)  # email в форме регистрации проверен на уникальность
            except Exception:
                user = False
            if user:
                subject = 'Запрошен сброс пароля'
                email_template_name = 'registration/password_reset_email.html'
                cont = {
                    "email": user.email,
                    'domain': '127.0.0.1:8000',  # доменное имя сайта
                    'site_name': 'FoodGram',  # название своего сайта
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # шифруем идентификатор
                    'user': user,
                    'token': default_token_generator.make_token(user),  # генерируем токен
                    'protocol': 'http',
                }
                msg_html = render_to_string(email_template_name, cont)
                try:
                    send_mail(subject, 'ссылка', settings.EMAIL_HOST_USER, [user.email], fail_silently=True,
                              html_message=msg_html)
                except BadHeaderError:
                    return HttpResponse('Обнаружен недопустимый заголовок!')
                return redirect('password_reset_done')
            else:
                messages.error(request, 'Пользователь не найден')
                return redirect('password_reset')
    return render(request, 'registration/password_reset_form.html')
