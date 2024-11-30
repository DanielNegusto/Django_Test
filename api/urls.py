from django.urls import path

from api.views import PhoneNumberView, VerificationCodeView, UserProfileView

urlpatterns = [
    path('auth/login/', PhoneNumberView.as_view(), name='login'),
    path('auth/verify/', VerificationCodeView.as_view(), name='verify'),
    path('profile/<str:phone_number>/', UserProfileView.as_view(), name='profile')
]
