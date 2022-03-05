from core.models import ActiveLogins, Merchant
from auth_backend.settings import SECRET_KEY
import jwt
from django.http import JsonResponse


def putMerchantInRequest(request):
    global payload
    access_token = request.COOKIES.get('access')
    payload = None
    if access_token is None:
        request.merchant = None
    else:
        try:
            # Don't care about the signature. Just get the user ID as well as ensure token is not tampered with
            payload = jwt.decode(access_token, SECRET_KEY, algorithms='[HS256]',
                                 options={"verify_exp": False})
        except jwt.InvalidSignatureError:
            request.merchant = None
        if payload is not None:
            request.merchant = Merchant.objects.filter(id=payload['id']).first()
    return request


def unauthorized_response(request, *args, **kwargs):
    return JsonResponse({"status": "FAILURE", "detail": "USER_NOT_AUTHENTICATED"})


class MerchantAuthenticationMiddleWare:
    def __init__(self, getResponse):
        self.getResponse = getResponse

    def __call__(self, request, *args, **kwargs):
        request = putMerchantInRequest(request)
        response = self.getResponse(request)
        return response


def gb_merchant_login_required(original_view):
    def login_decorator(request, *args, **kwargs):
        access_token = request.COOKIES.get('access')
        valid = ActiveLogins.objects.filter(token=access_token).exclude(merchant=None).first() is not None
        if not valid:
            return unauthorized_response(request, *args, **kwargs)
        return original_view(request, *args, **kwargs)

    return login_decorator
