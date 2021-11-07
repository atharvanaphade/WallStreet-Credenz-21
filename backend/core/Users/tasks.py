from celery import shared_task
from celery.utils.log import get_task_logger
import pandas as pd
from .models import *

news = pd.read_csv('news.csv')

logger = get_task_logger(__name__)

@shared_task 
def send_notifiction():
    logger.info("Yello!")



@shared_task()
def add_news():
    g_obj = Globals.objects.all().first()
    if g_obj.market_on and g_obj.start_news:
        global news
        new_news = news.iloc[g_obj.NewsCounter, :]
        title = new_news.title
        g_obj.LiveText = new_news.title
        description = new_news.description
        g_obj.NewsCounter += 1
        g_obj.save()
            
        News.objects.create(title=title, description=description)
    else:
        return


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

