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

def alterMoney(user, money, no_of_shares) -> None:
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

def addObjectToBuyTable(user, company, no_of_shares, bid_price) -> None:
    buy_obj = CompanyBuyTable()
    buy_obj.user_fk = Profile.objects.filter(user_id=user).first()
    buy_obj.company_fk = company
    buy_obj.no_of_shares = no_of_shares
    buy_obj.bid_price = bid_price
    buy_obj.save()

def userCompanyTransaction(company, buy_obj) -> int:
    # Update spread 
    global_obj = Globals.objects.all().first()
    global_obj.spread += ((buy_obj.bid_price - company.share_price) * min(buy_obj.no_of_shares, company.remaining_no_of_shares))
    global_obj.save()

    # Update company share price.
    company.share_price = buy_obj.bid_price
    company.share_price += int(min(buy_obj.no_of_shares, company.remaining_no_of_shares) * (buy_obj.bid_price - company.share_price) / 200)
    company.save()

    user = Profile.objects.all().filter(pk=buy_obj.user_fk.pk).first()

    # Add object to user shares table.
    user_share_obj = UserShare.objects.all().filter(user_fk=user, company_fk=company).first()
    if user_share_obj is not None:
        # If user already has shares of the company.
        user_share_obj.no_of_shares += min(buy_obj.no_of_shares, company.remaining_no_of_shares)
        user_share_obj.save()
    elif user_share_obj is None:
        # If user does not have shares of the company.
        UserShare.objects.create(
            user_fk=user,
            company_fk=company,
            no_of_shares=min(buy_obj.no_of_shares, company.remaining_no_of_shares)
        )
    
    if buy_obj.no_of_shares <= company.remaining_no_of_shares:
        # If all of user's buy request is completed add to user history table
        return 0
    # Add the remaining buy request to the buy table
    return 1

