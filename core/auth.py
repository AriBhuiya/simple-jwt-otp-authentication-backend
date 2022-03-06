from django.core.mail import send_mail
import threading
from .models import ActiveLogins


# sends otp to given mailID. Don't use directly. Use a async wrapper
def _sendOtp(otp, emailid):
    send_mail(
        'OTP for --- Login',
        f'Your OTP for --- Login is {otp.pk} and is valid for 15 minutes. If you did not try to login, kindly ignore this.',
        from_email=None,
        recipient_list=[emailid, ],
        fail_silently=False,
    )


# Wrapper for Handling OTP asyncronously
def handleSendOtp(user):
    user.generateOTP()
    t1 = threading.Thread(target=_sendOtp, args=(user.otp, user.email))
    t1.start()


def handleTokenRefresh(access_token, refresh_token):
    return ActiveLogins.RefreshAccessToken(access_token, refresh_token)




