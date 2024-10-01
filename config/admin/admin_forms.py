from captcha.fields import ReCaptchaField
from django.contrib.admin.forms import AdminAuthenticationForm


class AdminAuthWithCaptcha(AdminAuthenticationForm):
    captcha = ReCaptchaField()
