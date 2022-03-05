from rest_framework import serializers
from .models import User, NonVerifiedUser, ActiveLogins, Merchant


class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ['id', 'first_name', 'email']
        extra_kwargs = {
            "password": {'write_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'last_name']
        extra_kwargs = {
            "password": {'write_only': True}
        }


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class ActiveLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveLogins
        fields = ['id', 'last_login', 'auto_logout', 'device', 'os', 'location']


class NonVerifiedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonVerifiedUser
        fields = ['id', 'first_name', 'email', 'last_name']

    def create(self, validated_data):
        email_id = validated_data['email']
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
