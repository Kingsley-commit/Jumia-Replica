from django.urls import path
from .views import LoginView, RegistrationView, Logout


urlpatterns = [
    path('', LoginView.as_view(), name='account'),
    path('logout/', Logout.as_view(), name="logout"),
    path('register/', RegistrationView.as_view(), name="register")
] 