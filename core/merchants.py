from django.http import JsonResponse

from core.auth import handleSendOtp
from custom_middlewares.merchants import gb_merchant_login_required, putMerchantInRequest
from .Serializers import NonVerifiedUserSerializer, ActiveLoginSerializer, MerchantSerializer
from .models import Merchant, NonVerifiedUser, OTP, ActiveLogins
from rest_framework.response import Response


def handleMerchantLoginOtpGeneration(email_id):
    user = Merchant.objects.filter(email=email_id).first()
    if user is None:
        status = "FAILURE"
    elif not user.is_active:
        status = "BLOCKED"
    else:
        status = "SUCCESS"
        handleSendOtp(user)
    return {
        "emailId": email_id,
        "status": status
    }


def handleRegisterNewMerchant(request):
    email_id = request.data['email']
    user = Merchant.objects.filter(email=email_id).first()
    if user is not None:
        return handleMerchantLoginOtpGeneration(email_id)
    # save new user data
    new_user = NonVerifiedUser.objects.filter(email=email_id).first()
    if new_user is not None:
        new_user.delete()
    serializer = NonVerifiedUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_user = serializer.save()
    handleSendOtp(new_user)
    return {
        "emailId": email_id,
        "status": "SUCCESS"
    }


def handleMerchantLogin(request):
    email_id = request.data['email']
    otp = request.data['otp']
    global user
    user = NonVerifiedUser.objects.filter(email=email_id).first()
    if not user:
        user = Merchant.objects.filter(email=email_id).first()
    valid, msg = OTP.validateOTP(otp, user)  # handle otp validation and attempt count
    if valid and isinstance(user, NonVerifiedUser):  # Transfer from non-verified to verified
        user = user.transferToMerchant()
        assert isinstance(user, Merchant), "Unable to Register new User"
    response = Response()
    response.data = {
        'email': email_id,
        'status': msg
    }
    if valid:
        access_token, refresh_token = ActiveLogins.LoginUser(user, request, user_is_merchant=True)
        response.set_cookie('access', value=access_token, httponly=True)
        response.set_cookie('refresh', value=refresh_token, path='/auth/refresh', httponly=True)
    return response


@gb_merchant_login_required
def handleGetLoggedMerchantDevices(request):
    putMerchantInRequest(request)
    serializer = ActiveLoginSerializer(ActiveLogins.objects.filter(merchant=request.merchant), many=True)
    return Response(serializer.data)


@gb_merchant_login_required
def handleMerchantLogout(request):
    emailId = request.data.get('email')
    loginId = request.data.get('loginId')
    userId = request.data.get('userId')
    if userId is not None:
        emailId = Merchant.objects.filter(id=userId).first().email
    CODE, response = ActiveLogins.LogoutMerchant(request=request, emailid=emailId, ids=loginId, checkPermissions=True)
    response.data = {'status': CODE}
    return response


@gb_merchant_login_required
def requestValidation(request):
    user = request.merchant
    serializer = MerchantSerializer(user)
    response = {'status': "SUCCESS"}
    response.update(serializer.data)
    return JsonResponse(response)
