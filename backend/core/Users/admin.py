from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Profile)
admin.site.register(Company)
admin.site.register(News)
admin.site.register(UserHistory)
admin.site.register(CompanyBuyTable)
admin.site.register(CompanySellTable)
admin.site.register(UserShare)