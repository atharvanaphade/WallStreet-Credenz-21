from django.shortcuts import render
from rest_framework import permissions
from .serializers import *
from rest_framework import mixins, generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
# add this permission to allow signle sign in from one user  
from .permissions import IsPrivateAllowed

# Create your views here.
class CreateAccountView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (AllowAny, )
    

class UpdateDestroyAccount(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = AccountSerializer
    permission_classes = (IsAuthenticated, )
    
class NewsCreateListData(generics.ListCreateAPIView,):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (AllowAny, )

class NewsUpdateDestroyData(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = (IsAuthenticated, )

class CompanyCreateListView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAdminUser, )

class CompanyUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAdminUser, )

# TODO : 
#   Add JWT
#   Add Swagger  ----->done
#   Add Buy Sell Views (Priority q)





