import random
import time
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import (
    PhoneNumberSerializer,
    VerificationCodeSerializer,
    UserProfileSerializer,
)


class PhoneNumberView(APIView):
    def get(self, request):
        return render(request, "api/phone_number.html")

    def post(self, request):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            user, created = User.objects.get_or_create(phone_number=phone_number)

            if created:
                user.generate_invite_code()
                user.verification_code = str(random.randint(1000, 9999))
                user.save()

                time.sleep(2)

                print(
                    f"Код для {phone_number}: {user.verification_code}, Инвайт-код: {user.invite_code}"
                )

                if request.accepted_renderer.format == "json":
                    return Response(
                        {
                            "message": "Код отправлен",
                            "invite_code": user.invite_code,
                            "Ваш код": user.verification_code,
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return render(
                        request,
                        "api/login_success.html",
                        {
                            "message": f"Ваш код: {user.verification_code}. Вы будете перенаправлены на страницу верификации через 5 секунд.",
                            "phone_number": phone_number,
                        },
                    )
            else:
                if request.accepted_renderer.format == "json":
                    return Response(
                        {
                            "message": f"Пользователь уже зарегистрирован. Ваш код: {user.verification_code}."
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return render(
                        request,
                        "api/login_success.html",
                        {
                            "message": f"Пользователь уже зарегистрирован. Ваш код: {user.verification_code}.",
                            "phone_number": phone_number,
                        },
                    )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationCodeView(APIView):
    def get(self, request):
        return render(request, "api/verification_code.html")

    def post(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data["phone_number"]
            code = serializer.validated_data["code"]

            try:
                user = User.objects.get(phone_number=phone_number)
                if user.verification_code == code:
                    user.is_verified = True
                    user.save()
                    if request.accepted_renderer.format == "json":
                        return Response(
                            {
                                "message": "Успешная авторизация",
                                "phone_number": phone_number,
                            }
                        )
                    else:
                        return render(
                            request,
                            "api/success_verification.html",
                            {
                                "message": "Успешная авторизация. Вы будете перенаправлены на страницу профиля через 5 секунд.",
                                "phone_number": phone_number,
                            },
                        )
                return Response(
                    {"message": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST
                )
            except User.DoesNotExist:
                return Response(
                    {"message": "Пользователь не найден"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    def get(self, request, phone_number):
        if not phone_number:
            return Response(
                {"message": "Номер телефона не предоставлен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(phone_number=phone_number)
            serializer = UserProfileSerializer(user)
            if request.accepted_renderer.format == "json":
                return Response({"user": serializer.data}, status=status.HTTP_200_OK)
            else:
                return render(request, "api/profile.html", {"user": serializer.data})

        except User.DoesNotExist:
            return Response(
                {"message": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, phone_number):
        invite_code = request.data.get("invite_code")

        if not invite_code:
            return Response(
                {"message": "Необходим инвайт-код"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inviter = User.objects.get(invite_code=invite_code)

            user = User.objects.get(phone_number=phone_number)

            if user.activated_invite_code:
                return Response(
                    {"message": "Инвайт-код уже активирован"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.activated_invite_code = True
            user.save()

            inviter.activated_users.add(user)

            return Response(
                {"message": "Инвайт-код успешно активирован"}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"message": "Пользователь или инвайт-код не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )
