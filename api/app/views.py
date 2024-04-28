from django.shortcuts import render
from ..api.settings import firebase
from django.http import HttpResponse
from django.http import JsonResponse

from app.models import InstantMessage, Chat

database = firebase.database()

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
    pseudo-code
    dct = dict()
    for message in chat_id:
        dct[message_id] = message_text
    return JsonResponse(dct)
    '''
