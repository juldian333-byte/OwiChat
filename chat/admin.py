from django.contrib import admin
from .models import Conversation, Message, MessageReaction

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('name', 'conversation_type', 'created_by', 'created_at')
    list_filter = ('conversation_type', 'created_at')
    search_fields = ('name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'conversation', 'text', 'created_at', 'is_deleted')
    list_filter = ('created_at', 'is_deleted')
    search_fields = ('sender__username', 'text')
    readonly_fields = ('created_at', 'edited_at')

@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'emoji', 'created_at')
    list_filter = ('emoji', 'created_at')
    search_fields = ('user__username', 'emoji')
