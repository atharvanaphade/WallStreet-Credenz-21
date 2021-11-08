from django.contrib import admin
from .models import *



class CompanyBuyTableAdmin(admin.ModelAdmin):
    list_display = ("user_fk", "company_fk", "no_of_shares", "bid_price", "transaction_time")
    list_filter = ("company_fk", "user_fk")
    search_fields = (
        "user_fk",
        "company_fk",
    )

class CompanySellTableAdmin(admin.ModelAdmin):
    list_display = ("user_fk", "company_fk", "no_of_shares", "bid_price", "transaction_time")
    list_filter = ("company_fk", "user_fk")
    search_fields = (
        "user_fk",
        "company_fk",
    )
# Register your models here.

admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(News)
admin.site.register(UserHistory)
admin.site.register(CompanyBuyTable, CompanyBuyTableAdmin)
admin.site.register(CompanySellTable, CompanySellTableAdmin)
admin.site.register(UserShare)
admin.site.register(Globals)