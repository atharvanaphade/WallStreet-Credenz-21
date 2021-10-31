from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='My Project Title')

urlpatterns = [
    path('', schema_view),
    path('register/', CreateAccountView.as_view(), name='register'),
    path('edit_profile/<int:pk>', UpdateDestroyAccount.as_view(), name='edit-account'),
    path('news_create/', NewsCreateListData.as_view(), name='create-news'),
    path('news/<int:pk>', NewsUpdateDestroyData.as_view(), name="edit-news"),
    path('company', CompanyCreateListView.as_view(), name="company"),
    path('company/<int:pk>', CompanyUpdateDestroyView.as_view(), name="edit-company"),
]