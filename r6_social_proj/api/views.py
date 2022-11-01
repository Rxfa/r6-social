from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, get_object_or_404
from knox.views import LoginView as KnoxLoginView
from rest_framework import permissions, status
from rest_framework.authentication import (BasicAuthentication, TokenAuthentication)
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class LoginView(KnoxLoginView):
  authentication_classes = [BasicAuthentication]
  

class ListUsers(APIView):
    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        userSerializer = UserSerializer(data=request.data)
        if userSerializer.is_valid():
            user = userSerializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response({
            'message': userSerializer.errors, 'status': status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST
        )