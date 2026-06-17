#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'owichat.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile
from chat.models import Conversation

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@owichat.com', 'admin123')
    print(f"Superuser 'admin' created successfully!")
else:
    admin = User.objects.get(username='admin')
    print(f"Superuser 'admin' already exists")

# Create test users
test_users = [
    {'username': 'alice', 'first_name': 'Alice', 'last_name': 'Johnson'},
    {'username': 'bob', 'first_name': 'Bob', 'last_name': 'Smith'},
    {'username': 'charlie', 'first_name': 'Charlie', 'last_name': 'Brown'},
    {'username': 'diana', 'first_name': 'Diana', 'last_name': 'Prince'},
]

for user_data in test_users:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=f"{user_data['username']}@owichat.com",
            password='password123',
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        print(f"User '{user_data['username']}' created successfully!")
    else:
        user = User.objects.get(username=user_data['username'])
        print(f"User '{user_data['username']}' already exists")

# Create a test group conversation
users = list(User.objects.filter(username__in=['alice', 'bob', 'charlie']))
if users:
    group_name = "Web Development Team"
    if not Conversation.objects.filter(name=group_name, conversation_type='group').exists():
        group = Conversation.objects.create(
            name=group_name,
            conversation_type='group',
            created_by=users[0]
        )
        for user in users:
            group.participants.add(user)
        print(f"Group '{group_name}' created successfully!")
    else:
        print(f"Group '{group_name}' already exists")

print("\n✅ Setup completed successfully!")
print("Admin credentials: username=admin, password=admin123")
print("Test users: alice, bob, charlie, diana (password: password123)")
