from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'country', views.CountryAPI)
router.register(r'web/documents/upload', views.WebUploadDocumentsAPI)
router.register(r'documents/update', views.UpdateDocumentsAPI)

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('signup/', views.SignupAPI.as_view(), name='signup'),
    path('login/web/', views.WebLoginView.as_view(), name='login'),
    path('login/outlet/', views.OutletLoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('delete/', views.DeleteAccountAPI.as_view(), name='delete-account'),
    path('profile/', views.ProfileAPI.as_view(), name='profile'),
    path('verification/resend/', views.ResendVerificationAPI.as_view(), name='resend-verification'),
    path('verification/check/', views.OTPCheckAPI.as_view(), name='otp-check'),
    path('account/verify/', views.AccountVerifyAPI.as_view(), name='account-verify'),
    path('change/password/', views.PasswordChangeAPI.as_view(), name='change-password'),
    path('forget/password/', views.ForgetPasswordAPI.as_view(), name='forget-password'),
    path('forget/password/confirm/', views.ForgetPasswordConfirmAPI.as_view(), name='forget-password-confirm'),
    path('documents/upload/', views.UploadDocumentsAPI.as_view(), name='documents-upload'),
]
urlpatterns += router.urls
