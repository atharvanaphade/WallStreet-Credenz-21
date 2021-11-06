from .models import *

def checkUserhasMoney(user, money) -> bool:
    profile = Profile.objects.all().filter(user_id=user).first()
    if (profile.cash >= money):
        return True
    return False

def checkForCompanyShares(company, no_of_shares_requested) -> bool:
    if (company.remaining_no_of_shares >= no_of_shares_requested):
        return True
    return False

def alterMoney(user, money, no_of_shares):
    profile = Profile.objects.filter(user_id=user).first()
    profile.cash -= no_of_shares * money
    profile.save()
    
def checkIsBidValid(bid_price, company) -> bool:
    global_obj = Globals.objects.all().first()
    high = company.share_price + company.share_price * global_obj.bid_range
    low = company.share_price - company.share_price * global_obj.bid_range
    if (bid_price <= high and bid_price >= low):
        return True
    return False

def addObjectToBuyTable(user, company, no_of_shares, bid_price):
    
    # buy_obj = CompanyBuyTable.objects.create()
    buy_obj = CompanyBuyTable()
    buy_obj.user_fk = Profile.objects.filter(user_id=user).first()
    buy_obj.company_fk = company
    buy_obj.no_of_shares = no_of_shares
    buy_obj.bid_price = bid_price
    buy_obj.save()
            
    
    # user_fk = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # compnay_fk = models.ForeignKey(Company, on_delete=models.CASCADE)
    # no_of_shares = models.IntegerField(default=0)
    # bid_price = models.IntegerField(default=0)
    # transaction_time = models.DateTimeField(auto_now_add=True)co
