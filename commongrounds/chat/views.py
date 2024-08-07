# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Chat, Message
from django.contrib.auth.decorators import login_required
from core.models import Userprofile

@login_required
def chat_view(request, chat_id):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('/add_user')
    chat = get_object_or_404(Chat, id=chat_id)
    context["chat"] = chat
    return render(request, 'chat/chat.html', context)

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        chat = get_object_or_404(Chat, id=chat_id)
        user_message = Message.objects.create(sender="user", content=content, chat=chat)

        # Save chatbot response
        chatbot_message = Message.objects.create(sender="agent", content="response", chat=chat)
        
        return JsonResponse({
            'user_message': user_message.content,
            'chatbot_message': chatbot_message.content,
            'timestamp': chatbot_message.timestamp
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
