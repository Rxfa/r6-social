"""r6_social_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from knox import views as knox_views

from api.views import ListUsers, LoginView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r'api/auth/login/', LoginView.as_view(), name='knox_login'),
    path(r'api/auth/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path(r'api/auth/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]

urlpatterns += [
    path(r'api/users/', ListUsers.as_view(), name='list_users'),
]