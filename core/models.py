import datetime
import random
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
import jwt
import django as dj
from django.template.backends import django

from auth_backend.settings import SECRET_KEY, REFRESH_KEY
from rest_framework.response import Response


# Create your models here.
class OTP(models.Model):
    expiry = models.DateTimeField(null=False)
    attempts = models.IntegerField(default=5)
    digits = models.IntegerField(primary_key=True)

    @staticmethod
    def validateOTP(otp_digits, user):
        otp_actual = user.otp
        if otp_actual is None:
            return False, "INVALID_OTP"
        if user is None:
            return False, "USER_DOESNOT_EXIST"
        if not user.is_active:
            return False, "USER_BLOCKED"
        otp_actual.attempts -= 1
        otp_actual.save()
        if otp_actual.attempts == 0:
            otp_actual.delete()
            return False, "ATTEMPTS_EXCEEDED"
        if otp_digits == otp_actual.digits and (otp_actual.expiry - datetime.datetime.now()).total_seconds() > 0:
            user.otp.delete()
            return True, "SUCCESS"
        return False, "INVALID_OTP"


class User(AbstractUser):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    # password = models.CharField(max_length=255)
    otp = models.ForeignKey(OTP, null=True, default=None, on_delete=models.SET_NULL)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def validateOTP(self,
                    user_otp):  # Take otp and validate if backend otp and front end otp matches. Also decrease attempts and delete otp in each check
        otp = self.otp
        if otp is None:
            return False, -1
        if otp.digits != user_otp or (otp.expiry - datetime.datetime.utcnow()).total_seconds() < 0:
            return False, 1
        otp.delete()
        return True, 1

    def generateOTP(self):
        otp_digits = random.randint(100000, 999999)
        otp_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        otp = OTP(digits=otp_digits, expiry=otp_exp)
        otp.save()
        self.otp = otp
        self.save()
        return otp


class NonVerifiedUser(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=dj.utils.timezone.now)
    otp = models.ForeignKey(OTP, null=True, default=None, on_delete=models.SET_NULL)

    def toUser(self):
        user = User(first_name=self.first_name, last_name=self.last_name, email=self.email, is_active=self.is_active,
                    otp=self.otp)
        return user

    def toMerchant(self):
        merchant = Merchant(first_name=self.first_name, email=self.email, is_active=self.is_active,
                            otp=self.otp)
        return merchant

    def validateOTP(self,
                    user_otp):  # Take otp and validate if backend otp and front end otp matches. Also decrease attempts and delete otp in each check
        otp = self.otp
        if otp is None:
            return False
        otp.attempts -= 1
        otp.save()
        if otp.attempts == 0:
            otp.delete()
            self.is_active = False
            self.save()
        if otp.digits != user_otp or (otp.expiry - datetime.datetime.utcnow()).total_seconds() < 0:
            return False
        otp.delete()
        return True

    def generateOTP(self):
        otp_digits = random.randint(100000, 999999)
        otp_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        otp = OTP(digits=otp_digits, expiry=otp_exp)
        otp.save()
        self.otp = otp
        self.save()
        return otp

    def transferToUser(self):
        n_user = self.toUser()
        n_user.otp = None
        n_user.save()
        self.delete()
        return n_user

    def transferToMerchant(self):
        n_user = self.toMerchant()
        n_user.otp = None
        n_user.save()
        self.delete()
        return n_user


class Merchant(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False)
    is_active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    # password = models.CharField(max_length=255)
    otp = models.ForeignKey(OTP, null=True, default=None, on_delete=models.SET_NULL)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __repr__(self):
        return f'{self.id} | {self.email} | {self.first_name} '

    def validateOTP(self,
                    user_otp):  # Take otp and validate if backend otp and front end otp matches. Also decrease attempts and delete otp in each check
        otp = self.otp
        if otp is None:
            return False, -1
        if otp.digits != user_otp or (otp.expiry - datetime.datetime.utcnow()).total_seconds() < 0:
            return False, 1
        otp.delete()
        return True, 1

    def generateOTP(self):
        otp_digits = random.randint(100000, 999999)
        otp_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        otp = OTP(digits=otp_digits, expiry=otp_exp)
        otp.save()
        self.otp = otp
        self.save()
        return otp


class ActiveLogins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, db_index=True)
    merchant = models.ForeignKey(Merchant, on_delete=models.CASCADE, null=True)
    token = models.CharField(max_length=400, unique=True)
    refresh_token = models.CharField(max_length=400)
    last_login = models.DateTimeField(null=False)
    auto_logout = models.DateTimeField(null=False)
    device = models.CharField(max_length=1000)
    os = models.CharField(max_length=1000)
    location = models.CharField(max_length=100)

    @staticmethod
    def __generateAuthTokens(request, user):
        payload = {
            'id': str(user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }
        iat, exp = datetime.datetime.utcnow(), datetime.datetime.utcnow() + datetime.timedelta(days=365)
        refresh_payload = {
            "agent": request.META['HTTP_USER_AGENT'],
            'exp': exp,
            'iat': iat,
            'id': str(user.id)
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, REFRESH_KEY, algorithm="HS256")
        return access_token, refresh_token, iat, exp

    @staticmethod
    def LoginUser(user, request, user_is_merchant=False):
        access_token, refresh_token, iat, exp = ActiveLogins.__generateAuthTokens(request, user)
        if not user_is_merchant:
            login = ActiveLogins(user=user, merchant=None, token=access_token, refresh_token=refresh_token,
                                 last_login=iat,
                                 auto_logout=exp, device=request.META['HTTP_USER_AGENT'])
        else:
            login = ActiveLogins(user=None, merchant=user, token=access_token, refresh_token=refresh_token,
                                 last_login=iat,
                                 auto_logout=exp, device=request.META['HTTP_USER_AGENT'])
        login.save()
        return access_token, refresh_token

    @staticmethod
    def LogoutUser(emailid=None, ids=None, access_token=None, request=None, user_is_merchant=False,
                   checkPermissions=True):
        global login
        response = Response()
        login = None
        if ids is not None:
            if checkPermissions:
                login = ActiveLogins.objects.filter(user=request.user, id__in=ids) if type(ids) == type(
                    []) else ActiveLogins.objects.filter(id=ids)
            else:
                login = ActiveLogins.objects.filter(id__in=ids) if type(ids) == type(
                    []) else ActiveLogins.objects.filter(id=ids)
        elif emailid is not None:
            if checkPermissions:
                if request.user.email == emailid:
                    login = ActiveLogins.objects.filter(user=request.user)
                    response.delete_cookie('access')
                    response.delete_cookie('refresh')
            else:
                login = ActiveLogins.objects.filter(user=request.user)
        elif access_token is not None:
            login = ActiveLogins.objects.filter(token=access_token).first()
        elif request is not None:  # Delete from only Request, i.e, same device
            access_token = request.COOKIES.get('access')
            login = ActiveLogins.objects.filter(token=access_token).first()
            response.delete_cookie('access')
            response.delete_cookie('refresh')
        else:
            raise AttributeError("you must enter either of params")
        if login:
            login.delete()
            return "SUCCESS", response
        return "FAILURE", response

    @staticmethod
    def LogoutMerchant(emailid=None, ids=None, access_token=None, request=None,
                       checkPermissions=True):
        global login
        response = Response()
        login = None
        if ids is not None:
            if checkPermissions:
                login = ActiveLogins.objects.filter(merchant=request.merchant, id__in=ids) if type(ids) == type(
                    []) else ActiveLogins.objects.filter(id=ids)
            else:
                login = ActiveLogins.objects.filter(id__in=ids) if type(ids) == type(
                    []) else ActiveLogins.objects.filter(id=ids)
        elif emailid is not None:
            if checkPermissions:
                if request.user.email == emailid:
                    login = ActiveLogins.objects.filter(merchant=request.merchant)
                    response.delete_cookie('access')
                    response.delete_cookie('refresh')
            else:
                login = ActiveLogins.objects.filter(merchant=request.merchant)
        elif access_token is not None:
            login = ActiveLogins.objects.filter(token=access_token).first()
        elif request is not None:  # Delete from only Request, i.e, same device
            access_token = request.COOKIES.get('access')
            login = ActiveLogins.objects.filter(token=access_token).first()
            response.delete_cookie('access')
            response.delete_cookie('refresh')
        else:
            raise AttributeError("you must enter either of params")
        if login:
            login.delete()
            return "SUCCESS", response
        return "FAILURE", response

    @staticmethod
    def ValidateToken(token, expiry_check=True):
        try:
            if expiry_check:
                payload = jwt.decode(token, SECRET_KEY, algorithms='[HS256]')
            else:
                payload = jwt.decode(token, SECRET_KEY, algorithms='[HS256]',
                                     options={"verify_exp": False})
        except jwt.InvalidSignatureError:
            return False, None
        return True, payload

    @staticmethod
    def RefreshAccessToken(current_access_token, current_refresh_token):
        active_login = ActiveLogins.objects.filter(token=current_access_token,
                                                   refresh_token=current_refresh_token).first()
        if active_login is None:
            return active_login
        payload = {
            'id': str(active_login.user.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow()
        }

        access_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        active_login.token = access_token
        active_login.save()
        return access_token
