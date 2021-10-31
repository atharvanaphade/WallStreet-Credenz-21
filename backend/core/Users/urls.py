from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    path('register/', CreateAccountView.as_view(), name='register'),
    path('edit_profile/<int:pk>', UpdateDestroyAccount.as_view(), name='edit-account'),
    path('news_create/', NewsCreateListData.as_view(), name='create-news'),
    path('news/<int:pk>', NewsUpdateDestroyData.as_view(), name="edit-news"),
    path('company', CompanyCreateListView.as_view(), name="company"),
    path('company/<int:pk>', CompanyUpdateDestroyView.as_view(), name="edit-company"),
    path('buy/', BuyView.as_view(), name='buy-view'),
    path('get_token/', TokenObtainPairView.as_view(), name='get-token'),
    path('get_refresh/', TokenRefreshView.as_view(), name='get-refresh'),
]

# DRF-YASG
schema_view = get_schema_view(
   openapi.Info(
      title="WallStreet API",
      default_version='v1',
      description="Backend API for WallStreet Credenz '21",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
   path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]