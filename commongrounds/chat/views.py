# views.py
import threading
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Chat, Message
from django.template.loader import render_to_string
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

    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)

    context["chat"] = chat

    if request.method == 'POST':
        content = request.POST.get('content')
        response = chat.messages.last()
        if response.content == "✨ Thinking...":
            agent_message_html = render_to_string('chat/partials/error.html', {'error_message': "Please wait till previous request is processed", 'note':'Please refresh the page if it is taking too long'})
            return HttpResponse(agent_message_html)
        if content and content.strip():
            if Message.is_first_message_by_user(chat=chat, sender="user"):
                print("This is the first message by this user in this chat")
                # find relevant context
                system_message = Message.objects.create(sender="system", content="context:context", chat=chat)
            
            user_message = Message.objects.create(sender="user", content=content, chat=chat)
            user_message_html = render_to_string('chat/partials/message.html', {'message': user_message})
            agent_message = Message.objects.create(
                sender="agent", 
                content="✨ Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chat/partials/hot_response.html', {'message': agent_message})
            messages = user_message_html + agent_message_html
            
            thread = threading.Thread(target=llm_response, args=(agent_message.id,))
            thread.start()
            return HttpResponse(messages)

        return HttpResponse('Invalid request', status=400)

    return render(request, 'chat/chat.html', context)

@login_required
def get_response(request, chat_id):
    user_profile = Userprofile.objects.filter(user=request.user).first()
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)
    response = chat.messages.last()
    if response.content == "✨ Thinking...":
        response_html = render_to_string('chat/partials/hot_response.html',  {'message': response})
    else:
        response_html = render_to_string('chat/partials/response.html',  {'message': response})
    return HttpResponse(response_html)

def llm_response(messageid):
    # Wait for 5 seconds
    
    agent_message = Message.objects.get(id=messageid)
    agent_message.content = "This is a sample message that may be returned by the chatbot. The chatbot utilizes an advanced RAG based system for searching through and finding interesting people as per your liking!"
    agent_message.save()

@login_required
def create_chat(request, title):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('/add_user')

    chat = Chat.objects.create(
        title = title,
        user = user_profile
    )
    Message.objects.create(
        sender="system", 
        content="prompt",
        chat=chat
    )
    Message.objects.create(
        sender="agent", 
        content="✨ Welcome to commongrounds. What can I do for you!", 
        chat=chat
    )
    return redirect(f'/chat/{chat.id}')