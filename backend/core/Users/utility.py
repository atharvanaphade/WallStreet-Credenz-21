from models import Company
import pandas as pd

companies = pd.read_csv('Users/company_data.csv')

def setCompanyTempName():
    for i in Company.objects.all():
        i.short_name = ''.join(filter(str.isalnum, i.company_name))
        i.save()

    print("Temp Name Set!")

def add_companies(csvfile):
    company_data = pd.read_csv(companies)
    for cnt, i in enumerate(Company["name"]):
        print(i)
        Company.objects.create(company_name=i, share_price=company_data["sharePrice"][cnt], total_no_shares=company_data["numberOfShares"][cnt], remaining_no_of_shares=company_data["numberOfShares"][cnt])

    setCompanyTempName()

add_companies()