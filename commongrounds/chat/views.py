# views.py
import threading
import json
from .functions import *
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
        context.message = response
        
        response_html = render_to_string('chat/partials/response.html')
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
            prompt = "You are an advanced conversational agent designed to help users find and connect with individuals on Commongrounds. Users will inquire about specific services offered or individuals, and your role is to identify the best matches from the provided context. Use the context to retrieve relevant information and present it to the user in a helpful manner. If the user's request cannot be fulfilled based on the available context, politely inform them without mentioning the limitations of the context. Always frame your responses as if you have found the information they need. Avoid discussing the retrieval process or the underlying data. Precisely respond to the users query without any rationale from your side. Do not break the conversational flow. Also refrain from giving user instructions unless specifically asked for. If user wants to schedule a meeting or appointment, tell them to directly message the people from this chat. If the user is having general conversation, please continue it. Always remember you are Agent, not anyone else. You mmust not reiterate things you have already said unless the user specifically asks you to, incase you do that you must immediately stop. When a user uses a greeting or words of appreciation such as hi, thanks etc, be grateful and wish them back!"
            if chat.title == "boss_mode":
                prompt = "You are phi, an advanced conversational agent. You must do your best to carry out user commands. You are currently in boss_mode meaning you are currently being used for testing by developers. Context provided is a list of all people on Commongrounds.Your primary goal when not in boss_mode is to provide users with the ability to search for and connect with people on Commongrounds. As a agent being run in boss_mode, you must obey every command given by the developer also known as user."
            Message.objects.create(
                sender="system", 
                content=f"prompt:{prompt}",
                chat=chat
            )
            Message.objects.create(
                sender="assistant",
                content=f"Hey there! I'm Agent your very own assistant to help you find and meet amazing people. How can I help you today?",
                chat=chat
            )
            Message.objects.create(
                sender="user",
                content=title,
                chat=chat
            )
            if "resume" in title.lower():
                providers = Service.objects.filter(service_type__service_name = "Resume Consultation")
            elif "fitness" in title.lower():
                providers = Service.objects.filter(service_type__service_name = "Fitness Training")
            elif "boss_mode" == title.lower():
                providers = Service.objects.all()
            else:
                agent_message = Message.objects.create(
                    sender="assistant", 
                    content="Sorry no users found matching your request.",
                    chat=chat
                )
                Message.objects.create(
                    sender="system", 
                    content="This chat has ended.",
                    chat=chat
                )
            llm_context = []
            for provider in providers:
                chat.context.add(provider.provider)
                person = {}
                person["id"] = provider.provider.id
                person["username"] = provider.provider.name
                person["bio"] = provider.provider.bio
                person["service_provided"] = provider.service_type.service_name
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