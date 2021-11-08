from re import U
from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

# Create serializers here.


class AccountSerializer(serializers.ModelSerializer):
    class ProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = Profile
            fields = ()

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'profile']
    
    @staticmethod
    def create(validated_data):
        print(validated_data)
        user_instance = User.objects.create_user(**validated_data)
        if 'profile' in validated_data.keys():
            profile_data = validated_data.pop('profile')
            Profile.objects.create(user_id=user_instance, **profile_data)
        else:
            Profile.objects.create(user_id=user_instance)
        return user_instance

class SecureProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class CompanySerializer(serializers.ModelSerializer):

    bid_shares = serializers.IntegerField(default=0)
    bid_price = serializers.IntegerField(default=0)
    company_name = serializers.CharField(default='')

    class Meta:
        model = Company
        exclude = ["remaining_no_of_shares","total_no_shares", "share_price", "short_name"]
        # fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"

class SellViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShare
        fields = ["company_name", "short_name", "share_price", "remaining_no_of_shares"]

class GetAllNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["news_title", "description"]

class UserStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ["user_id", "rank"]
        extra_kwargs = {
            "user_company_shares" : {"required": True, "read_only": False}
        }