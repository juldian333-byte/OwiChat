from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from .models import Conversation, Message, MessageReaction
import json

@login_required(login_url='users:login')
def chat_list(request):
    conversations = request.user.conversations.all().prefetch_related('participants')
    
    for conv in conversations:
        last_message = conv.messages.filter(is_deleted=False).last()
        conv.last_message = last_message
    
    return render(request, 'chat/chat_list.html', {'conversations': conversations})

@login_required(login_url='users:login')
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    
    if request.user not in conversation.participants.all():
        return redirect('chat:chat_list')
    
    messages = conversation.messages.filter(is_deleted=False).select_related('sender').prefetch_related('reactions')
    
    return render(request, 'chat/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages,
    })

@login_required(login_url='users:login')
def start_conversation(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        recipient = get_object_or_404(User, id=recipient_id)
        
        conversation = Conversation.objects.filter(
            conversation_type='private',
            participants=request.user
        ).filter(participants=recipient).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                conversation_type='private',
                created_by=request.user
            )
            conversation.participants.add(request.user, recipient)
        
        return redirect('chat:conversation_detail', pk=conversation.id)
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/start_conversation.html', {'users': users})

@login_required(login_url='users:login')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        participant_ids = request.POST.getlist('participants')
        
        conversation = Conversation.objects.create(
            name=group_name,
            conversation_type='group',
            created_by=request.user
        )
        conversation.participants.add(request.user)
        
        for participant_id in participant_ids:
            user = get_object_or_404(User, id=participant_id)
            conversation.participants.add(user)
        
        if 'avatar' in request.FILES:
            conversation.group_avatar = request.FILES['avatar']
            conversation.save()
        
        return redirect('chat:conversation_detail', pk=conversation.id)
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_group.html', {'users': users})

@login_required(login_url='users:login')
@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    messages = conversation.messages.filter(is_deleted=False).select_related('sender').prefetch_related('reactions')
    
    messages_data = []
    for msg in messages:
        reactions = {}
        for reaction in msg.reactions.all():
            if reaction.emoji not in reactions:
                reactions[reaction.emoji] = []
            reactions[reaction.emoji].append(reaction.user.username)
        
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'text': msg.text,
            'image': msg.image.url if msg.image else None,
            'created_at': msg.created_at.isoformat(),
            'reactions': reactions
        })
    
    return JsonResponse({'messages': messages_data})

@login_required(login_url='users:login')
@require_POST
def send_message(request):
    conversation_id = request.POST.get('conversation_id')
    text = request.POST.get('text', '')
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    message = Message.objects.create(
        conversation=conversation,
        sender=request.user,
        text=text
    )
    
    if 'image' in request.FILES:
        message.image = request.FILES['image']
        message.save()
    
    if 'file' in request.FILES:
        message.file = request.FILES['file']
        message.save()
    
    return JsonResponse({
        'id': message.id,
        'sender': message.sender.username,
        'text': message.text,
        'created_at': message.created_at.isoformat(),
        'image': message.image.url if message.image else None,
        'file': message.file.url if message.file else None,
    })

@login_required(login_url='users:login')
@require_POST
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    
    if message.sender != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    message.is_deleted = True
    message.save()
    
    return JsonResponse({'success': True})
