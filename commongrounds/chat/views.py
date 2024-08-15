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
    context["chat"] = chat
    return render(request, 'chat/chat.html', context)

@login_required
def get_response(request, message):
    message = get_object_or_404(Message, id=message)
    chat = get_object_or_404(Chat, id=message.chat.id)
    response = chat.messages.last()
    if response.content == "✨ Thinking...":
        response_html = render_to_string('chat/partials/response.html',  {'message': response})
    else:
        response_html = render_to_string('chat/partials/message.html',  {'message': response})
    return HttpResponse(response_html)

def llm_response(messageid):
    # Wait for 5 seconds
    time.sleep(5)
    agent_message = Message.objects.get(id=messageid)
    agent_message.content = "This is a sample message that may be returned by the chatbot. The chatbot utilizes an advanced RAG based system for searching through and finding interesting people as per your liking!"
    agent_message.save()

@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        chat = get_object_or_404(Chat, id=chat_id)
        
        if content and content.strip():
            user_message = Message.objects.create(sender="user", content=content, chat=chat)

            # Render the user's message
            user_message_html = render_to_string('chat/partials/message.html', {'message': user_message})
            agent_message = Message.objects.create(
                sender="agent", 
                content="✨ Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chat/partials/response.html', {'message': agent_message})

            # Combine the HTML for the response
            messages = user_message_html + agent_message_html
            
            # Start a thread for handling the chatbot response
            thread = threading.Thread(target=llm_response, args=(agent_message.id,))
            thread.start()

            # Respond with the combined HTML immediately
            return HttpResponse(messages)

    return HttpResponse('Invalid request', status=400)
