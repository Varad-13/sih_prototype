# views.py
import threading
import json
from .functions import *
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Chat, Message
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from core.models import Userprofile
from huggingface_hub import InferenceClient

@login_required
def chat_view(request, chat_id):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('onboarding')

    chat = get_object_or_404(Chat, id=chat_id)

    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)
    context["chat"] = chat

    if request.method == 'POST':
        content = request.POST.get('content')
        response = chat.messages.last()
        if response.content == "Thinking...":
            agent_message_html = render_to_string('chat/partials/error.html', {'error_message': "Please wait till previous request is processed", 'note':'Please refresh the page if it is taking too long'})
            return HttpResponse(agent_message_html)
        if content and content.strip():
            if len(content) > 500:
                agent_message_html = render_to_string(
                    'chat/partials/error.html',
                    {
                        'error_message': "Message exceeds character limit",
                        'note':'Maximum prompt length is 500 characters'
                    }
                )
                return HttpResponse(agent_message_html)

            user_message = Message.objects.create(sender="user", content=content, chat=chat)
            user_message_html = render_to_string('chat/partials/message.html', {'message': user_message})
            agent_message = Message.objects.create(
                sender="assistant", 
                content="Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chat/partials/hot_response.html', {'message': agent_message})
            messages = user_message_html + agent_message_html
            message_history = chat.messages.all()
            thread = threading.Thread(target=llm_response, args=(agent_message.id,message_history,))
            thread.start()
            return HttpResponse(messages)
        else:
            return HttpResponse('Invalid request', status=400)
    
    message = chat.messages.last()
    if message and message.content == "Thinking...":
        messages = chat.messages.all()
        thread = threading.Thread(target=llm_response, args=(message.id,messages,))
        thread.start()
        return render(request, 'chat/new_chat.html', context)
    elif message and message.content == "This chat has ended." and message.sender == "system":
        return render(request, 'chat/chat_ended.html', context)
    return render(request, 'chat/chat.html', context)

@login_required
def get_response(request, chat_id):
    user_profile = Userprofile.objects.filter(user=request.user).first()
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)
    response = chat.messages.last()
    if response.content == "Thinking...":
        response_html = render_to_string('chat/partials/hot_response.html',  {'message': response})
    else:
        context = {}
        context["message"] = response
        for user in chat.context.all():
            if user.name in response.content:
                response.context.add(user)
        response_html = render_to_string('chat/partials/response.html', context)
    return HttpResponse(response_html)

def llm_response(messageid, messages):
    message_history = []
    for m in messages:
        message = {}
        message["role"] = m.sender
        message["content"] = m.content
        message_history.append(message)
    try:
        client = InferenceClient(
            "microsoft/Phi-3-mini-4k-instruct",
            token="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",
        )
        response = client.chat_completion(
                messages=message_history,
                max_tokens=500,
                stream=False,
            )
        agent_message = Message.objects.get(id=messageid)
        response_message = parse_markdown(response.choices[0].message.content)
        agent_message.content = response.choices[0].message.content
        agent_message.content_html = response_message
        agent_message.save()
    except:
        agent_message = Message.objects.get(id=messageid)
        agent_message.sender = "system"
        agent_message.content = "Something went wrong while generating response"
        agent_message.save()

def create_chat(request):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('onboarding')
    if request.method == 'POST':
        if request.POST.get('title').strip():
            title = request.POST.get('title')
            chat = Chat.objects.create(
                title = request.POST.get('title'),
                user = user_profile
            )
            prompt = "You are an advanced conversational agent designed to help employees with questions related to HR Policies, IT Support and Organizational events. Relevant information will be provided by system as context. Only respond based on the context and avoid giving opinions. Keep all information factual and correct."
            Message.objects.create(
                sender="system", 
                content=f"prompt:{prompt}",
                chat=chat
            )
            Message.objects.create(
                sender="assistant",
                content=f"Hey there! I'm Agent your very own assistant to help you with HR Policies. How can I help you today?",
                chat=chat
            )
            Message.objects.create(
                sender="user",
                content=title,
                chat=chat
            )
            agent_message = Message.objects.create(
                sender="assistant", 
                content="Thinking...",
                chat=chat
            )
            response = HttpResponse()
            response["HX-Redirect"] = f'/chat/{chat.id}'
            return response
        else:
            return 
    return render(request, 'core/index.html', context)