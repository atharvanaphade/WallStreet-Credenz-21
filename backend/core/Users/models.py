from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Globals(models.Model):
    sensex = models.FloatField(default=0)
    spread = models.IntegerField(default=0)
    bid_range = models.FloatField(default=0)
    market_on = models.BooleanField(default=True)
    start_news = models.BooleanField(default=True)
    news_counter = models.IntegerField(default=0)

class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.IntegerField(default=-1)
    no_of_shares = models.IntegerField(default=0)
    cash = models.IntegerField(default=200000)
    net_worth = models.IntegerField(default=0) # 60 % share valuation 40 % cash valuation
    
    def __str__(self) -> str:
        return self.user_id.username + "'s Profile" 

class Company(models.Model):
    company_name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=8)
    share_price = models.IntegerField(default=0)
    total_no_shares = models.IntegerField(default=0)
    remaining_no_of_shares = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.company_name + '_' + str(self.share_price)

class News(models.Model):
    news_title = models.TextField(max_length=300, default="NA")
    description = models.TextField(max_length=4000, default="NA")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.news_title

class UserHistory(models.Model):
    user_fk = models.ForeignKey(Profile,related_name="user_fk", on_delete=models.CASCADE)
    company_fk = models.ForeignKey(Company,related_name="company_fk", on_delete= models.CASCADE)
    no_of_shares = models.IntegerField(default=0)
    bid_price = models.IntegerField(default=0)
    buy_or_sell = models.BooleanField(default=False)
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user_fk.user_id.username + '_' + self.company_fk.company_name

class CompanyBuyTable(models.Model):
    user_fk = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE)
    no_of_shares = models.IntegerField(default=0)
    bid_price = models.IntegerField(default=0)
    transaction_time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.user_fk.user_id.username + '_' + self.company_fk.company_name + '_BuyRow'

class CompanySellTable(models.Model):
    user_fk = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company_fk = models.ForeignKey(Company, on_delete=models.CASCADE)
    no_of_shares = models.IntegerField(default=0)
    bid_price = models.IntegerField(default=0)
    transaction_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.user_fk.user_id.username + '_' + self.company_fk.company_name + '_SellRow'


class UserShare(models.Model):
    user_fk = models.ForeignKey(Profile, on_delete=models.CASCADE)
    company_fk = models.ForeignKey(Company, on_delete= models.CASCADE)
    no_of_shares = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.user_fk.user_id.username}_{self.company_fk.company_name}_UserShare_{self.no_of_shares}'
    