from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from custom_middlewares.merchants import putMerchantInRequest, gb_merchant_login_required
from .Serializers import UserSerializer, MerchantSerializer
from .users import handleLoginOtpGeneration, handleRegisterNewUser, handleLogin, handleLogout, handleGetLoggedDevices
from .auth import handleTokenRefresh
from custom_middlewares.users import gb_user_login_required, putUserInRequest
from django.views.decorators.csrf import csrf_exempt
from .merchants import handleRegisterNewMerchant, handleMerchantLogin, handleMerchantLoginOtpGeneration, \
    handleGetLoggedMerchantDevices, handleMerchantLogout


@gb_user_login_required
def home(request):
    return HttpResponse(f"{request.user}OK")


@gb_merchant_login_required
def merchant_home(request):
    return HttpResponse(f"{request.merchant}OK")


@gb_user_login_required
def userProfile(request):
        user = request.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data)


@method_decorator(csrf_exempt, name='dispatch')
class RefreshView(APIView):
    def post(self, request):
        access_token, refresh_token = request.COOKIES.get('access'), request.COOKIES.get('refresh')
        new_access_token = handleTokenRefresh(access_token, refresh_token)
        response = Response()
        if new_access_token is not None:
            response.data = {"STATUS": "SUCCESS"}
            response.set_cookie("access", new_access_token)
            return response
        response.data = {"STATUS": "FAILURE"}
        response.delete_cookie("access")
        response.delete_cookie("refresh", path='/auth/refresh')
        return response


class UserViewNew(APIView):
    def post(self, request):
        request_type = request.data['requestType']
        if request_type == "REGISTER_NEW_USER":
            return Response(handleRegisterNewUser(request))
        elif request_type == "LOGIN":
            return handleLogin(request)  # returns Response Object and auto sets cookies in response object.
        elif request_type == "LOGOUT":
            putUserInRequest(request)
            return handleLogout(request)

    def get(self, request):
        request_type = request.GET.get('requestType')
        if request_type == 'LOGIN_OTP_GENERATION':
            email_id = request.GET['email']
            return Response(handleLoginOtpGeneration(email_id))
        elif request_type == 'LOGGED_DEVICES':
            return handleGetLoggedDevices(request)
        raise AuthenticationFailed("Bad Request")


class TestView(APIView):
    def get(self, request):
        putUserInRequest(request)
        return HttpResponse(f"{request.user}")


@gb_user_login_required
def requestValidation(request):
    user = request.user
    serializer = UserSerializer(user)
    response = {'status': "SUCCESS"}
    response.update(serializer.data)
    return JsonResponse(response)


@gb_merchant_login_required
def merchantRequestValidation(request):
    user = request.merchant
    serializer = MerchantSerializer(user)
    response = {'status': "SUCCESS"}
    response.update(serializer.data)
    return JsonResponse(response)


class MerchantView(APIView):
    def post(self, request):
        request_type = request.data['requestType']
        if request_type == "REGISTER_NEW_MERCHANT":
            request.data['last_name'] = 'MERCHANT'
            return Response(handleRegisterNewMerchant(request))
        elif request_type == "LOGIN":
            return handleMerchantLogin(request)  # returns Response Object and auto sets cookies in response object.
        elif request_type == "LOGOUT":
            putMerchantInRequest(request)
            return handleMerchantLogout(request)

    def get(self, request):
        request_type = request.GET.get('requestType')
        if request_type == 'LOGIN_OTP_GENERATION':
            email_id = request.GET['email']
            return Response(handleMerchantLoginOtpGeneration(email_id))
        elif request_type == 'LOGGED_DEVICES':
            return handleGetLoggedMerchantDevices(request)
        raise AuthenticationFailed("Bad Request")
