import os
from .models import InstantMessage, Chat, User, UserToChat
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout, login, update_session_auth_hash
from rest_framework.views import APIView
from rest_framework.generics import (RetrieveUpdateAPIView, 
    CreateAPIView)
from .serializers import (UserSerializer, UserLoginSerializer)
from .permissions import IsNotAuthenticated, CustomIsAuthenticated
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


def chat_json(request, chat_id):
    '''
    !!! implement check if user is allowed to read this chat here !!!
    pseudo-code
    dct = dict()
    for message in chat_id:
        dct[message_id] = message_text
    return JsonResponse(dct)
    '''
    message_to_user_and_text = dict()
    message_to_user_and_text["messages"] = []
    for message in InstantMessage.objects.filter(chat=chat_id):
        message_to_user_and_text["messages"].append([message.id, message.user.id, message.text, message.date_added])
    return JsonResponse(message_to_user_and_text)


class UserRegisterView(CreateAPIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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


class UserEditView(RetrieveUpdateAPIView):
    permission_classes = (CustomIsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.get_serializer(
            instance=request.user)
        data = serializer.data
        data.pop('password')
        return Response(data=data,
                        status=status.HTTP_200_OK)
    
    def get_queryset(self):
        return self.request.user

    def update(self, request):
        serializer = self.get_serializer(instance=request.user, 
                                        data=request.data, 
                                        partial=True)
        if serializer.is_valid(raise_exception=True):
            user = serializer.update(request.user, 
                                    serializer.validated_data)
            update_session_auth_hash(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SendMessageView(APIView):
    permission_classes = (CustomIsAuthenticated,)

    def post(self, request, chat_id: int):
        chat = Chat.objects.get(id=chat_id)
        message_text = request.data.get('message')
        if not message_text:
            return Response(
                data={'error': "You can't send empty message."},
                status=status.HTTP_400_BAD_REQUEST
            )
        message = InstantMessage(text=message_text,
                            chat=chat, user=request.user)
        message.save()

        return Response(status=status.HTTP_200_OK)


class AllUserChatsView(APIView):
    permission_classes = (CustomIsAuthenticated,)

    def get(self, request):
        user_to_chats = request.user.user_to_chat.all()
        data = {}
        for user_to_chat in user_to_chats:
            chat = user_to_chat.chat
            try:
                last_message = chat.messages.latest('date_added').text
            except InstantMessage.DoesNotExist:
                last_message = ''
            data[chat.id] = [chat.title, last_message]
        return Response(data=data, status=status.HTTP_200_OK)
    

class CreateChatView(APIView):
    permission_classes = (CustomIsAuthenticated,)

    def post(self, request):
        try:
            username = request.data.get('username')
            if request.user.username == username:
                raise ValueError("You can't create a chat with yourself.")
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                data={'error': "User with this username doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as e:
            return Response(
                data={'error': e},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chat_type = request.data.get('chat_type')
        users_list = request.data.get('users')
        if chat_type == 0:
            if len(users_list) > 1:
                return Response(
                    data={
                        'error': 'Private chat is only for two users.'
                    }, status=status.HTTP_400_BAD_REQUEST
                )
            private_chats_1 = set(
                request.user.user_to_chat.values_list('chat_id')
            )
            private_chats_2 = set(
                user.user_to_chat.values_list('chat_id')
            )
            if private_chats_1 & private_chats_2:
                return Response(
                    data={
                        'error': 'You already have private chat with this user'
                    }, status=status.HTTP_400_BAD_REQUEST
                )

        chat_title = request.data.get('title')
        chat = Chat.objects.create(title=chat_title, 
                                chat_type=chat_type)
        UserToChat(chat=chat, user=request.user).save()
        for username in users_list:
            user = User.objects.get(username=username)
            UserToChat(chat=chat, user=user).save()

        return Response(status=status.HTTP_200_OK)