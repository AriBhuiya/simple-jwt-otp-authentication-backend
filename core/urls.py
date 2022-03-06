"""gdwb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('merchant', views.merchant_home, name='merchant_homw'),
    path('refresh', views.RefreshView.as_view(), name='refresh'),
    path('user/profile/', views.userProfile,name='userview'),
    path('user/', views.UserViewNew.as_view(),name='userview_new'),
    path('merchant/', views.MerchantView.as_view(),name='merchant_view'),
    path('request-validation',views.requestValidation,name='request_validation'),
    path('merchant-request-validation',views.merchantRequestValidation,name='merchant-request_validation'),
    path('test/',views.TestView.as_view())
]
