"""cryptech URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from django.contrib import admin
from django.urls import path
from . import views
from . import api_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('keys/', views.keys, name='keys'),
    path('login_user/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('upload/', views.upload, name='upload'),
    path('test/', views.test, name='test'),
    path('origin/', views.origin, name='origin'),
    path('explore/', views.explore, name='explore'),
    path('', views.upload, name='upload'),
    path('verify/', views.verify, name='verify'),
    path('register/', views.UserFormView.as_view(), name='register'),
    path('check/', views.check, name='check'),
    path('generate_key_pair', api_views.generate_key_pair),
    path('publish', api_views.publish),
    path('publish_with_notary', api_views.publish_with_notary),
    path('verify_sign', api_views.verify_sign),
    path('verify_sign_notary', api_views.verify_sign_notary),
    path('get_published_data', api_views.get_published_data),

]
