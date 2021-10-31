from django.shortcuts import render
from rest_framework import permissions
from .serializers import *
from rest_framework import mixins, generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.response import Response

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

class BuyView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    permission_classes = (IsAuthenticated, )
    
    def get(self, request, *args, **kwargs):
        global_obj = Globals.objects.get(pk=1)
        ret_dict = {}
        if global_obj.market_on:
            companies = Company.objects.all()
            ret_dict['companies'] = []
            for company in companies:
                temp = {}
                if company.remaining_no_of_shares > 0:
                    temp['company_name'] = company.company_name
                    temp['short_name'] = company.short_name
                    temp['share_price'] = company.share_price
                    temp['remaining_no_of_shares'] = company.remaining_no_of_shares
                    ret_dict['companies'].append(temp)
            ret_dict['sensex'] = global_obj.sensex
            ret_dict['bid_range'] = global_obj.bid_range
            return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)
    
    def post(self, request, *args, **kwargs):
        global_obj = Globals.objects.get(pk=1)
        ret_dict = {}
        if global_obj.market_on:
            try:
                copmany_name = request.data['company_name']
                bid_shares = request.data['bid_shares']
                bid_price = request.data['bid_price']

                # TODO :

                # create functions for all below !!

                # check if user has money, company has shares, and if bid is valid

                # if valid remove money from user profile

                # add object to buy table
            except:
                ret_dict['status'] = 'INVALID_DATA'
                return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)

# TODO : 
#   Add JWT --> Done
#   Add Swagger  ----->done
#   Add Buy Sell Views (Priority q)







