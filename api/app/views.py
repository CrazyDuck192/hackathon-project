import os
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from app.models import InstantMessage, Chat
from django.contrib.auth import logout, login
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer, UserLoginSerializer
from .permissions import IsNotAuthenticated, CustomIsAuthenticated
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import (SessionAuthentication, 
                                        authenticate)

def index(request):
    return render(request, 'index.html')


def staticfiles(request, filename):
    static_path = os.path.join(os.path.abspath(__file__), "..", "..", "..", "static")
    with open(os.path.join(static_path, filename), 'r') as f:
        file_data = f.read()
        response = HttpResponse(file_data)
        if (filename.split('.')[-1] == 'js'):
            response['Content-Type'] = 'application/javascript; charset=utf-8'
        if (filename.split('.')[-1] == 'css'):
            response['Content-Type'] = 'text/css; charset=utf-8'
    return response


def chat(request):
    return render(request, 'chat.html')


def chat_json(request, chat_id):
    '''
    !!! implement check if user is allowed to read this chat here !!!
    pseudo-code
    dct = dict()
    for message in chat_id:
        dct[message_id] = message_text
    return JsonResponse(dct)
    '''

    
class UserRegisterView(APIView):
    permission_classes = (IsNotAuthenticated,)

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(serializer.validated_data)
            if user:
                return Response(
                    status=status.HTTP_200_OK
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class UserAuthenticateView(APIView):
    permission_classes = (IsNotAuthenticated,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(request, **serializer.validated_data)
            if user is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

class UserLogoutView(APIView):
    permission_classes = (CustomIsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    permission_classes = (CustomIsAuthenticated,)

    def post(self, request):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)

        return Response(status=status.HTTP_200_OK)