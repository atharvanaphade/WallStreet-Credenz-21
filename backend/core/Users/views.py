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

class GetAllNewsView(generics.ListCreateAPIView):
    serializer_class = GetAllNewsSerializer
    permission_classes = (AllowAny, )
    queryset = News.objects.all()

class BuyView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, )
    queryset = Company.objects.all()
    
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
                bid_shares = int(request.data['bid_shares'])
                bid_price = int(request.data['bid_price'])
                company_obj = Company.objects.filter(company_name=company_name).first()
                if (checkUserhasMoney(request.user, int(bid_price)) and 
                checkForCompanyShares(company_obj, int(bid_shares)) and 
                checkIsBidValid(int(bid_price), company_obj)):
                    addObjectToBuyTable(request.user, company_obj,
                    int(bid_shares), int(bid_price))
                    alterMoney(request.user, int(bid_price), int(bid_shares))
                    # TODO: match utilities
                    ret_dict['status'] = 'Bid Placed!'
                    return Response(ret_dict, status=201)
                
            except Exception as e:
                ret_dict['status'] = f'error is {e}'
                return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)
        



class SellView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, )
    
    def get_queryset(self, request):
        pro_obj = Profile.objects.filter(user_id = request.user).first()
        share_obj = UserShare.objects.filter(user_fk = pro_obj)
        return share_obj


    def get(self, request):
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on:
            pro_obj = Profile.objects.filter(user_id = request.user).first()

            user_share_list = UserShare.objects.filter(user_fk = pro_obj)

            ret_dict['share_list'] = []
            for obj in user_share_list:
                temp = {}
                
                temp['company_name'] = obj.company_fk.company_name
                temp['short_name'] = obj.company_fk.short_name
                temp['share_price'] = obj.company_fk.share_price
                temp['no_of_shares'] = obj.no_of_shares
                ret_dict['share_list'].append(temp)
            
            return Response(ret_dict, status=200)

        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)

    def post(self, request, *args, **kwargs):
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on:
            try:
                company_name = str(request.data['company_name'])
                bid_shares = int(request.data['bid_shares'])
                bid_price = int(request.data['bid_price'])
                
                pro_obj = Profile.objects.filter(user_id = request.user).first()
                com_obj = Company.objects.filter(company_name=company_name).first()
                available_share = UserShare.objects.filter(company_fk=com_obj, user_fk=pro_obj).first()
                
                
                if(checkIsBidValid(bid_price, com_obj)):
                    if (bid_shares < available_share.no_of_shares):
                        available_share.no_of_shares -= bid_shares
                        available_share.save()
                    elif (bid_shares == available_share.no_of_shares):
                        available_share.delete()

                    CompanySellTable.objects.create(
                        user_fk = pro_obj,
                        company_fk = com_obj,
                        no_of_shares = bid_shares,
                        bid_price = bid_price
                        )      

                    # Todo matching utility

                    ret_dict['status'] = 'Valid Bid'
                    return Response(ret_dict, status=200)

                else:
                    ret_dict['status'] = 'Invalid Bid'
                    return Response(ret_dict, status=200)

            except Exception as e:
                ret_dict['status_error'] = str(e)
                return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)
