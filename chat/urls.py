from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('conversation/<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('new/', views.start_conversation, name='start_conversation'),
    path('create-group/', views.create_group, name='create_group'),
    path('api/messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
    path('api/send/', views.send_message, name='send_message'),
    path('api/delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
]
