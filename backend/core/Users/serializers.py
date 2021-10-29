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
    class Meta:
        model = Company
        fields = "__all__"


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"
        