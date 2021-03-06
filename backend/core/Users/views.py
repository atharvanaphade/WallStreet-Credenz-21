from tempfile import tempdir
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import *
from .tasks import match_util
from .utils import *
from rest_framework import pagination

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

class CompanygetListView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny, )


class CompanygetListView(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny, )

class CompanyUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (IsAdminUser, )

class GetCompanyView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = (AllowAny, )

class GetAllNewsView(generics.ListCreateAPIView):
    serializer_class = GetAllNewsSerializer
    permission_classes = (AllowAny, )
    queryset = News.objects.all().order_by('-time')

@api_view(['GET'])
def GetLeaderBoard(request):
    all_profs = Profile.objects.all().order_by('-net_worth')
    ret_dict = {}
    ret_dict['persons'] = []
    for item in all_profs:
        temp={}
        temp['name'] = item.user_id.get_username()
        temp['net_worth'] = item.net_worth
        ret_dict['persons'].append(temp)
    return Response(ret_dict, status=200)
    serializer_class = LeaderBoardSerializer
    permission_classes = (AllowAny, )
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50


@api_view(['GET'])
def getLiveText(request):
    live_text = News.objects.all().order_by('-time').first().news_title
    return Response({"live_text": live_text}, status=200)

class BuyView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()
    
    @permission_classes((AllowAny, ))
    def get(self, request, *args, **kwargs):
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on:
            companies = Company.objects.all()
            ret_dict['companies'] = []
            for company in companies:
                temp = {}
                temp['id'] = company.id
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
    
    @permission_classes((IsAuthenticated, ))
    def post(self, request, *args, **kwargs):
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on == True:
            try:
                company_name = request.data['company_name']
                bid_shares = int(request.data['bid_shares'])
                bid_price = int(request.data['bid_price'])
                company_obj = Company.objects.filter(
                    company_name=company_name).first()
                if (checkUserhasMoney(request.user, int(bid_price*bid_shares)) and
                    checkForCompanyShares(company_obj, int(bid_shares)) and
                        checkIsBidValid(int(bid_price), company_obj)):
                    addObjectToBuyTable(request.user, company_obj,
                                        int(bid_shares), int(bid_price))
                    alterMoney(request.user, int(bid_price), int(bid_shares))
                    # TODO: match utilities testing
                    match_util.delay(company_obj.pk)
                    ret_dict['status'] = 'Bid Placed!'
                    return Response(ret_dict, status=201)
                else:
                    ret_dict['status'] = "Invalid Bid!"
                    return Response(ret_dict, status=200)
            except Exception as e:
                ret_dict['status'] = f'error is {e}'
                return Response(ret_dict, status=200)
        ret_dict['status'] = 'MKT_CLOSED'
        return Response(ret_dict, status=200)


class SellView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self, request):
        pro_obj = Profile.objects.filter(user_id=request.user).first()
        share_obj = UserShare.objects.filter(user_fk=pro_obj)
        return share_obj

    def get(self, request):
        global_obj = Globals.objects.all().first()
        ret_dict = {}
        if global_obj.market_on:
            pro_obj = Profile.objects.filter(user_id=request.user).first()

            user_share_list = UserShare.objects.filter(user_fk=pro_obj)

            ret_dict['share_list'] = []
            for obj in user_share_list:
                temp = {}
                temp['id'] = obj.company_fk.pk
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

                pro_obj = Profile.objects.filter(user_id=request.user).first()
                com_obj = Company.objects.filter(
                    company_name=company_name).first()
                available_share = UserShare.objects.filter(
                    company_fk=com_obj, user_fk=pro_obj).first()

                if(checkIsBidValid(bid_price, com_obj)):
                    if (bid_shares < available_share.no_of_shares):
                        available_share.no_of_shares -= bid_shares
                        available_share.save()
                    elif (bid_shares == available_share.no_of_shares):
                        available_share.delete()

                    CompanySellTable.objects.create(
                        user_fk=pro_obj,
                        company_fk=com_obj,
                        no_of_shares=bid_shares,
                        bid_price=bid_price
                    )

                    # TODO: matching utility testing
                    match_util.delay(com_obj.pk)

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


class GetUserStatsView(generics.ListCreateAPIView):
    serializer_class = UserStatsSerializer
    queryset = Profile.objects.all()
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        query_dict = {}
        try:
            user_share_qs = UserShare.objects.filter(
                user_fk=Profile.objects.filter(user_id=request.user).first())
            user = Profile.objects.filter(user_id=request.user).first()
            user_share_hist = UserHistory.objects.filter(
                user_fk=Profile.objects.filter(user_id=request.user).first()
            )

            query_dict["no_of_shares"] = user.no_of_shares
            query_dict["cash"] = user.cash
            query_dict["net_worth"] = user.net_worth
            query_dict["rank"]=user.rank
            query_dict["company_user_share_list"] = []
            query_dict['Completed_trans']=[]
            query_dict['pending_trans']=[]

            for user_share in user_share_qs:
                temp_dict = {}
                company = user_share.company_fk
                temp_dict = {"company_name": company.company_name,
                             "no_of_shares": user_share.no_of_shares
                             }
                query_dict["company_user_share_list"].append(temp_dict)
            
            for trans in user_share_hist:
                temp_dict={}
                test = "Sell"
                if(trans.buy_or_sell):

                    test="Buy"

                temp_dict = {
                    'Company' : trans.company_fk.company_name,
                    'Type' : test,
                    'no_of_shares' : trans.no_of_shares,
                    'bid_price' : trans.bid_price

                }
                query_dict["Completed_trans"].append(temp_dict)
            
            profile = Profile.objects.get(user_id=request.user)
            sell_objects = CompanySellTable.objects.filter(user_fk=profile)
            buy_objects = CompanyBuyTable.objects.filter(user_fk=profile)

            for buy in buy_objects:
                temp = {
                    "Company": buy.company_fk.company_name,
                    "Type": "Buy",
                    "no_of_shares": buy.no_of_shares,
                    "bid_price": buy.bid_price
                }
                query_dict['pending_trans'].append(temp)

            for sell in sell_objects:
                temp = {
                    "Company": sell.company_fk.company_name,
                    "Type": "Sell",
                    "no_of_shares": sell.no_of_shares,
                    "bid_price": sell.bid_price
                }
                query_dict['pending_trans'].append(temp)
                
            query_dict["status"] = "Successfully fetched user data..!!"
            return Response(query_dict, status=200)
        except Exception as e:
            query_dict["status"] = f"not working error found = {e}"
            return Response(query_dict, status=404)

    # rank
    # vauational
    # cash holding
    # share holding
    # purn profile
