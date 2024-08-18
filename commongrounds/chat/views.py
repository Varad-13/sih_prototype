# views.py
import threading
import time
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Chat, Message
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from core.models import Userprofile, Service
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
                sender="agent", 
                content="Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chat/partials/hot_response.html', {'message': agent_message})
            messages = user_message_html + agent_message_html
            chat_history = Message.objects.all()
            message_history = []
            for m in chat_history:
                message = {}
                message["role"] = m.sender
                message["content"] = m.content
                message_history.appent(message)
            thread = threading.Thread(target=llm_response, args=(agent_message.id,message_history))
            thread.start()
            return HttpResponse(messages)
        else:
            return HttpResponse('Invalid request', status=400)
    
    message = chat.messages.last()
    if message and message.sender == "user":
        if "resume" in message.content.lower():
            providers = Service.objects.filter(service_type__service_name = "resume consultation")
        elif "fitness" in message.content.lower():
            providers = Service.objects.filter(service_type__service_name = "Fitness Training")
        else:
            print("triggered")
            agent_message = Message.objects.create(
                sender="agent", 
                content="Sorry no users found matching your request.",
                chat=chat
            )
            Message.objects.create(
                sender="system", 
                content="This chat has ended.",
                chat=chat
            )
            return render(request, 'chat/chat_ended.html', context)
        llm_context = []
        for provider in providers:
            person = {}
            person["username"] = provider.provider.name
            person["bio"] = provider.provider.bio
            person["service_description"] = provider.description
            person["rate_per_hour"] = provider.rate
            llm_context.append(person)
        context_str = json.dumps(llm_context, indent=4)
        Message.objects.create(
            sender="system",
            content=f"context:\n{context_str}",
            chat=chat
        )
        agent_message = Message.objects.create(
            sender="agent", 
            content="Thinking...",
            chat=chat
        )
        messages = chat.messages.all()
        message_history = []
        for m in messages:
            message = {}
            message["role"] = m.sender
            message["content"] = m.content
            message_history.append(message)
        thread = threading.Thread(target=llm_response, args=(agent_message.id,message_history))
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
        response_html = render_to_string('chat/partials/response.html',  {'message': response})
    return HttpResponse(response_html)

def llm_response(messageid, messages):
    try:
        print("Started")
        client = InferenceClient(
            "microsoft/Phi-3-mini-4k-instruct",
            token="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",
        )
        response = client.chat_completion(
                messages=messages,
                max_tokens=500,
                stream=False,
            )
        agent_message = Message.objects.get(id=messageid)
        agent_message.content = response.choices[0].message.content
        agent_message.save()
        print(response.choices[0].message.content)
    except:
        agent_message = Message.objects.get(id=messageid)
        agent_message.sender = "system"
        agent_message.content = "Something went wrong while generating response"

@login_required
def create_chat(request):
    context = {}
    if request.user.is_authenticated:
        user_profile = Userprofile.objects.filter(user=request.user).first()
        if user_profile:
            context['userprofile'] = user_profile
        else:
            return redirect('onboarding')
    if request.method == 'POST':
        if request.POST.get('title'):
            title = request.POST.get('title')
            chat = Chat.objects.create(
                title = request.POST.get('title'),
                user = user_profile
            )
            Message.objects.create(
                sender="system", 
                content="prompt:You are an advanced conversational agent designed to help users find and connect with individuals on Commongrounds. Users will inquire about specific services offered or individuals, and your role is to identify the best matches from the provided context. Use the context to retrieve relevant information and present it to the user in a helpful manner. If the user's request cannot be fulfilled based on the available context, politely inform them without mentioning the limitations of the context. Always frame your responses as if you have found the information they need. Avoid discussing the retrieval process or the underlying data. Precisely respond to the users query without any rationale from your side. Do not break the conversational flow. Also refrain from giving user instructions unless specifically asked for. If user wants to schedule a meeting or appointment, tell them to directly message the people from this chat.",
                chat=chat
            )
            Message.objects.create(
                sender="agent",
                content=f"Hey there! I'm Agent your very own assistant to help you find and meet amazing people. How can I help you today?",
                chat=chat
            )
            Message.objects.create(
                sender="user",
                content=title,
                chat=chat
            )
            response = HttpResponse()
            response["HX-Redirect"] = f'/chat/{chat.id}'
            return response
    return render(request, 'core/index.html', context)