from celery import shared_task
from celery.utils.log import get_task_logger
import pandas as pd
from .models import *
from .utils import *

# news = pd.read_csv('news.csv')

logger = get_task_logger(__name__)

@shared_task 
def send_notifiction():
    logger.info("Yello!")



# @shared_task()
# def add_news():
#     g_obj = Globals.objects.all().first()
#     if g_obj.market_on and g_obj.start_news:
#         global news
#         new_news = news.iloc[g_obj.NewsCounter, :]
#         title = new_news.title
#         g_obj.LiveText = new_news.title
#         description = new_news.description
#         g_obj.NewsCounter += 1
#         g_obj.save()
            
#         News.objects.create(title=title, description=description)
#     else:
#         return


@shared_task()
def spread_task():
    profiles = {}
    total_transaction = 0

    g_obj = Globals.objects.all().first()

    for p in Profile.objects.all():
        profiles[p] = 0

    for u in UserHistory.objects.all():
        value = u.no_of_shares * u.bid_price
        total_transaction += value

        profiles[u.profile] += value

    for p in Profile.objects.all():
        spreadRatio = profiles[p] / total_transaction
        p.cash += (spreadRatio * g_obj.spread)
        p.save()

    g_obj.spred = 0
    g_obj.save()

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
                elif (sell_pointer < len(sell_objects)) and company.share_price < sell_objects[sell_pointer].bid_price and buy_objects[buy_pointer] >= company.share_price:
                    
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