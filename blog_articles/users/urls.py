from django.urls import path
from django.views.generic import TemplateView   # ← Ajoute cette ligne en haut si pas déjà présente

from users.views.dashboard_views import DashboardView
from users.views.home_view import HomeView
from users.views.contact_view import ContactView
from users.views.admin_view import AdminDashboardView
from users.views.user_views import UserCreateView, UserEditView, UserDeleteView, UserDetailView
from users.api.viewsets import UserListAPI
from rest_framework_simplejwt.views import TokenRefreshView
from users.views.login_view import LoginAPIView, LoginPageView, LogoutView
from users.views.signup_view import SignupPageView, SignupAPIView, VerifyOTPView

app_name = 'users'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', SignupPageView.as_view(), name='register'),
    path('login/', LoginPageView.as_view(), name='login'),

    # API
    path('api/register/', SignupAPIView.as_view(), name='register_api'),
    path('api/login/', LoginAPIView.as_view(), name='api-login'),

    # Activation OTP
    path('api/verify-otp/', VerifyOTPView.as_view(), name='api_verify_otp'),
    
    # PAGE DE VÉRIFICATION OTP (nouvelle URL)
    path('verify-otp/', TemplateView.as_view(template_name='users/verify_otp.html'), name='verify_otp_page'),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:id>/edit/', UserEditView.as_view(), name='user_edit'),
    path('users/<int:id>/delete/', UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),
    path('api/users/', UserListAPI.as_view(), name='user_list'),
]