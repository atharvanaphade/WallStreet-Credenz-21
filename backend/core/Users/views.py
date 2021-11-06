from django.shortcuts import render
from rest_framework import permissions
from rest_framework import mixins, generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import *
from .utils import *

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
        global_obj = Globals.objects.all().first()
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
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on:
            try:
                company_name = request.data['company_name']
                bid_shares = request.data['bid_shares']
                bid_price = request.data['bid_price']
                company_obj = Company.objects.filter(company_name=company_name).first()
                if (checkUserhasMoney(request.user, bid_price) and 
                checkForCompanyShares(company_obj, bid_shares) and 
                checkIsBidValid(bid_price, company_obj)):
                    addObjectToBuyTable(request.user, company_obj,
                    bid_shares, bid_price)
                    alterMoney(request.user, bid_price, bid_shares)
                    # TODO: check against sell table
                    ret_dict['status'] = 'Bid Placed!'
                    return Response(ret_dict, status=201)
            except Exception as e:
                ret_dict['status'] = f'{e}'
                return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)

# TODO : 
#   Add JWT --> Done
#   Add Swagger  ----->done
#   Add Buy View (Priority q) --> Done
#   Add Sell View
#   Add News Tasks







