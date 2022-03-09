# return success or failure response by creating otp
from rest_framework.renderers import JSONRenderer

from core.auth import handleSendOtp
from .models import User, NonVerifiedUser, OTP, ActiveLogins
from .Serializers import NonVerifiedUserSerializer, ActiveLoginSerializer
from custom_middlewares.users import putUserInRequest
from rest_framework.response import Response
from custom_middlewares.users import gb_user_login_required


# generates and mail otp for existing users.
def handleLoginOtpGeneration(email_id):
    user = User.objects.filter(email=email_id).first()
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


# creates a temp user and sends otp
def handleRegisterNewUser(request):
    email_id = request.data['email']
    user = User.objects.filter(email=email_id).first()
    if user is not None:
        return handleLoginOtpGeneration(email_id)
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


def handleLogin(request):
    email_id = request.data['email']
    otp = request.data['otp']
    global user
    user = NonVerifiedUser.objects.filter(email=email_id).first()
    if not user:
        user = User.objects.filter(email=email_id).first()
    valid, msg = OTP.validateOTP(otp, user)  # handle otp validation and attempt count
    if valid and isinstance(user, NonVerifiedUser):  # Transfer from non-verified to verified
        user = user.transferToUser()
        assert isinstance(user, User), "Unable to Register new User"
    response = Response()
    response.data = {
        'email': email_id,
        'status': msg
    }
    if valid:
        access_token, refresh_token = ActiveLogins.LoginUser(user,request)
        response.set_cookie('access', value=access_token, httponly=True)
        response.set_cookie('refresh', value=refresh_token, path='/auth/refresh', httponly=True)

    return response


# Prone to csrf. Fix Later
@gb_user_login_required
def handleLogout(request):
    emailId = request.data.get('email')
    loginId = request.data.get('loginId')
    userId = request.data.get('userId')
    if userId is not None:
        emailId = User.objects.filter(pk=userId).first().email
    CODE,response = ActiveLogins.LogoutUser(request = request, emailid=emailId,ids=loginId, checkPermissions=True)
    response.data = {'status': CODE}
    return response

@gb_user_login_required
def handleGetLoggedDevices(request):
    putUserInRequest(request)
    serializer = ActiveLoginSerializer(ActiveLogins.objects.filter(user=request.user),many=True)
    return Response(serializer.data)


