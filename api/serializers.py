from rest_framework import serializers
from .models import User


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=4)


class UserProfileSerializer(serializers.ModelSerializer):
    activated_users = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['phone_number', 'is_verified', 'invite_code', 'activated_invite_code', 'activated_users']


class ActivateInviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)
