from datetime import datetime
from celery import shared_task
from celery.utils.log import get_task_logger
import pandas as pd
import pytz
from .models import *
from .utils import *

news = pd.read_csv('Users/news.csv')

logger = get_task_logger(__name__)

@shared_task 
def send_notifiction():
    logger.info("Yello!")


@shared_task()
def add_news():
    global_ = Globals.objects.all().first()
    if global_.market_on and global_.start_news:
        global news
        new_news = news.iloc[global_.news_counter%len(news['title']), :]
        title = new_news.title
        description = new_news.description
        global_.news_counter += 1
        global_.save()
            
        News.objects.create(news_title=title, description=description)
    else:
        return


@shared_task()
def spread_task():
    global_ = Globals.objects.all().first()
    if global_.market_on :
        profiles = {}
        total_transaction = 0
        for p in Profile.objects.all():
            profiles[p] = 0

        for u in UserHistory.objects.all():
            value = u.no_of_shares * u.bid_price
            total_transaction += value

            profiles[u.user_fk] += value

        for p in Profile.objects.all():
            spreadRatio = profiles[p] / total_transaction
            p.cash += (spreadRatio * global_.spread)
            p.save()

        global_.spread = 0
        global_.save()

@shared_task
def match_util(company_id):
    company = Company.objects.all().filter(pk=company_id).first()

    # Get buy and sell table objects in sorted order.
    buy_objects = CompanyBuyTable.objects.all().order_by('-bid_price', 'transaction_time')
    sell_objects = CompanySellTable.objects.all().order_by('bid_price', 'transaction_time')

    # If buy objects exists.
    if buy_objects is not None:
        buy_pointer = 0   # Iterator counter for buy objects.
        sell_pointer = 0  # Iterator counter for sell objects.

        while (buy_pointer < len(buy_objects)) and (sell_pointer < len(sell_objects) or company.remaining_no_of_shares):
            # Match buy tabl entries till request gets completed
            
            if company.remaining_no_of_shares:
                # Company has shares remaining
                
                if not (sell_pointer < len(sell_objects)):
                    if buy_objects[buy_pointer].bid_price >= company.share_price:
                        fl = userCompanyTransaction(company, buy_objects[buy_pointer])
                        buy_pointer += (fl == 0)
                        continue
                # If company.share_price is lesser than sell_object price sell shares of the company.
                elif (sell_pointer < len(sell_objects)) and company.share_price < sell_objects[sell_pointer].bid_price and buy_objects[buy_pointer].bid_price >= company.share_price:
                    
                    # Match buy bid to company.
                    fl = userCompanyTransaction(company, buy_objects[buy_pointer])
                    buy_pointer += (fl == 0) # Buy counter will be updated only if entry is deleted.
                    continue
            
            if (sell_pointer < len(sell_objects)) and sell_objects and buy_objects[buy_pointer].bid_price >= sell_objects[sell_pointer].bid_price:
                # Bid matched from buy table to sell table.
                fl = userTransaction(company, buy_objects[buy_pointer], sell_objects[sell_pointer])
                buy_pointer += (fl == -1 or fl == 0)
                sell_pointer += (fl == 1 or fl == 0)
            else:
                break

@shared_task
def processQueriesTask():
    # Iterate for all companies and process the buy sell objects for each company.
    companies = Company.objects.all()
    buy_objects = CompanyBuyTable.objects.all()
    sell_objects = CompanySellTable.objects.all()
    buy_pointer = 0
    sell_pointer = 0
    for company in companies:
        buy_pointer = 0   # Buy object iterator
        sell_pointer = 0  # Sell object iterator
        if CompanyBuyTable.objects.all() is not None:
            while buy_pointer < len(buy_objects) and (sell_pointer < len(sell_objects) or company.remaining_no_of_shares > 0):
                if company.remaining_no_of_shares > 0:
                    # Company has shares remaining
                    if not sell_pointer < len(sell_objects):
                        # If sell table does not have any objects, check for company shares.
                        fl = userCompanyTransaction(company, buy_objects[buy_pointer])
                        buy_pointer += (fl == 0)
                        continue
                    elif sell_pointer < len(sell_objects) and company.share_price < buy_objects[buy_pointer].bid_price and sell_objects[sell_pointer >= company.share_price]:
                        # If shares are left in table, but company share price is less than sell table, sell shares of the company.
                        fl = userCompanyTransaction(company, buy_objects[buy_pointer])
                        buy_pointer += (fl == 0)
                        continue
                if sell_pointer < len(sell_objects) and sell_objects and buy_objects[buy_pointer].bid_price >= sell_objects[sell_pointer].bid_price:
                    # Match buy object with sell object.
                    fl = userTransaction(company, buy_objects[buy_pointer], sell_objects[sell_pointer])
                    buy_pointer += (fl == -1 or fl == 0)
                    sell_pointer += (fl == 1 or fl == 0)
                else:
                    break
    
    # Delete buy/sell objects if not matched after a specific time, and return money to user.
    
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now().astimezone(tz)
    while (buy_pointer < len(buy_objects)):
        if (current_time - buy_objects[buy_pointer].transaction_time).seconds >= 150:
            userRevoke(buy_objects[buy_pointer], True)
            buy_objects.get(pk = buy_objects[buy_pointer].pk).delete()
        buy_pointer += 1

    while (sell_pointer < len(sell_objects)):
        if (current_time - sell_objects[sell_pointer].transaction_time).seconds >= 150:
            userRevoke(sell_objects[sell_pointer], False)
            sell_objects.get(pk = sell_objects[sell_pointer].pk).delete()
        sell_pointer += 1

@shared_task
def updateNetWorth():
    get_users = Profile.objects.all()
    for user in get_users:
        user.net_worth = 0
        user.save()
        get_user_shares = UserShare.objects.filter(user_fk = user)
        for user_share in get_user_shares:
            no_of_shares = user_share.no_of_shares
            company = Company.objects.filter(pk = user_share.company_fk.pk).first()
            user.net_worth += (0.6 * company.share_price * no_of_shares)
        user.net_worth += 0.4 * user.cash
        user.save()
    
