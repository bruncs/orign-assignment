from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from risk_profile.views import RiskProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('profile/', RiskProfileView.as_view(), name='profile')
]
