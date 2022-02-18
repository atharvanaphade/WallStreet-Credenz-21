from .models import *

def checkUserhasMoney(user, money) -> bool:
    profile = Profile.objects.all().filter(user_id=user).first()
    if (profile.cash >= money):
        return True
    return False

def checkForCompanyShares(company, no_of_shares_requested) -> bool:
    if (company.remaining_no_of_shares >= 0 and no_of_shares_requested > 0):
        return True
    return False

def alterMoney(user, money, no_of_shares) -> None:
    profile = Profile.objects.filter(user_id=user).first()
    profile.cash -= no_of_shares * money
    profile.save()

def alterSellMoney(user, money, no_of_shares) -> None:
    # profile = Profile.objects.filter(user_fk=user).first()
    user.cash += money * no_of_shares
    user.save()
    
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
    print(company.share_price)
    company.share_price = company.share_price + int(min(buy_obj.no_of_shares, company.remaining_no_of_shares) * (buy_obj.bid_price - company.share_price) / 200)
    print(company.share_price)
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
        UserHistory.objects.create(
            user_fk = user,
            company_fk = company,
            no_of_shares = buy_obj.no_of_shares,
            bid_price = buy_obj.bid_price,
            buy_or_sell = True,
        )
        company.remaining_no_of_shares -= buy_obj.no_of_shares
        company.save()
        CompanyBuyTable.objects.all().filter(pk=buy_obj.pk).first().delete()
        return 0
    # Add the remaining buy request to the buy table
    buy_obj.no_of_shares -= company.remaining_no_of_shares
    buy_obj.save()

    UserHistory.objects.create(
        user_fk = user,
        company_fk = company,
        no_of_shares = company.remaining_no_of_shares,
        bid_price = buy_obj.bid_price,
        buy_or_sell = True 
    )

    company.remaining_no_of_shares = 0
    company.save()
    return 1

def userTransaction(company, buy_obj, sell_obj) -> int:
    
    # Update spread
    global_obj = Globals.objects.all().first()
    global_obj.spread -= ((buy_obj.bid_price - sell_obj.bid_price) * min(buy_obj.no_of_shares, sell_obj.no_of_shares))
    global_obj.save()

    # Update company share price
    print("in user tran" + str(sell_obj.bid_price))
    company.share_price = sell_obj.bid_price
    company.save()

    buy_user = Profile.objects.all().filter(pk=buy_obj.user_fk.pk).first()   # Selling bid user
    sell_user = Profile.objects.all().filter(pk=sell_obj.user_fk.pk).first() # Buying bid user

    # Check if buying user has shares of given company.
    user_share = UserShare.objects.all().filter(user_fk=buy_user.pk).first()
    if user_share is not None: # User has shares.
        user_share.no_of_shares += min(buy_obj.no_of_shares, sell_obj.no_of_shares)
        user_share.save()
    if user_share is None: # User does not have shares.
        UserShare.objects.create(
            user_fk = buy_user,
            company_fk = company,
            no_of_shares = min(buy_obj.no_of_shares, sell_obj.no_of_shares)
        )
    
    if buy_obj.no_of_shares == sell_obj.no_of_shares: # If buying and selling bid are equal match bid and create user history
        # Create user history
        UserHistory.objects.create(
            user_fk = buy_user,
            company_fk = company,
            no_of_shares = buy_obj.no_of_shares,
            bid_price = buy_obj.bid_price,
            buy_or_sell = True
        )
        UserHistory.objects.create(
            user_fk = sell_user,
            company_fk = company,
            no_of_shares = sell_obj.no_of_shares,
            bid_price = sell_obj.bid_price,
            buy_or_sell = False
        )

        # Remove buy and sell table objects
        CompanyBuyTable.objects.get(pk=buy_obj.pk).delete()
        CompanySellTable.objects.get(pk=sell_obj.pk).delete()
        alterSellMoney(sell_user, sell_obj.bid_price, sell_obj.no_of_shares)
        return 0

    elif buy_obj.no_of_shares > sell_obj.no_of_shares: # If buying bid has more number of shares.
        # Update sell table entry
        buy_obj.no_of_shares -= sell_obj.no_of_shares
        buy_obj.save()

        # Create user history
        UserHistory.objects.create(
            user_fk = buy_user,
            company_fk = company,
            no_of_shares = buy_obj.no_of_shares,
            bid_price = buy_obj.bid_price,
            buy_or_sell = True
        )
        UserHistory.objects.create(
            user_fk = sell_user,
            company_fk = company,
            no_of_shares = sell_obj.no_of_shares,
            bid_price = sell_obj.bid_price,
            buy_or_sell = False
        )

        # Delete sell table obj
        CompanySellTable.objects.get(pk=sell_obj.pk).delete()
        alterSellMoney(sell_user, sell_obj.bid_price, sell_obj.no_of_shares)
        return 1
    
    # Number of buy shares are less than any sell request
    sell_obj.no_of_shares -= buy_obj.no_of_shares
    sell_obj.save()

    # Create user history
    UserHistory.objects.create(
        user_fk = buy_user,
        company_fk = company,
        no_of_shares = buy_obj.no_of_shares,
        bid_price = buy_obj.bid_price,
        buy_or_sell = True
    )
    UserHistory.objects.create(
        user_fk = sell_user,
        company_fk = company,
        no_of_shares = sell_obj.no_of_shares,
        bid_price = sell_obj.bid_price,
        buy_or_sell = False
    )

    # Delete sell table obj
    CompanySellTable.objects.get(pk=sell_obj.pk).delete()
    alterSellMoney(sell_user, sell_obj.bid_price, sell_obj.no_of_shares)
    return -1

def userRevoke(tableEntry, buySell):
    # Return money to user of buy objet stays too long in the table.
    user = tableEntry.user_fk
    company = Company.objects.get(pk = tableEntry.company_fk.pk)
    bid_price = tableEntry.bid_price
    no_of_shares = tableEntry.no_of_shares

    if buySell:
        alterMoney(user, bid_price * no_of_shares)
    else:
        try:
            u = UserShare.objects.get(company_fk=company, user_fk=user)
            u.no_of_shares += no_of_shares
            u.save()
        except:
            UserShare.objects.create(user_fk=user, company_fk=company, no_of_shares=no_of_shares)
