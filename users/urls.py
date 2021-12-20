from django.contrib.auth import views
from django.urls import path

from .views import LoginUser, SignUp, password_reset_request

urlpatterns = [
    path("signup/", SignUp.as_view(), name="signup"),
    path('login/', LoginUser.as_view(), name='login'),
    path('password_reset/', password_reset_request, name="password_reset"),
    path('password_reset/done/',
         views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]