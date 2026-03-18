import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from accounts.models import CustomUser
from .models import Message
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time chat"""
    
    async def connect(self):
        # Get the username from URL parameters
        self.username = self.scope['url_route']['kwargs'].get('username', '')
        self.user = self.scope['user']

        if self.user.is_anonymous or not self.username:
            await self.close()
            return

        self.room_name = f"chat_{min(self.user.username, self.username)}_{max(self.user.username, self.username)}"
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark user as online
        await self.mark_user_online(self.user)
        
        # Notify other user that this user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_online',
                'username': self.user.username
            }
        )

    async def disconnect(self, close_code):
        if getattr(self.user, 'is_anonymous', True):
            return

        # Mark user as offline
        await self.mark_user_offline(self.user)
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify other user that this user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_offline',
                'username': self.user.username
            }
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            message_type = data.get('type', 'message')
            
            if message_type in {'message', 'chat_message'} and message:
                # Save message to database
                await self.save_message(message)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': self.user.username,
                        'timestamp': datetime.now().isoformat()
                    }
                )
            elif message_type == 'typing':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_message',
                        'user': self.user.username,
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    async def chat_message(self, event):
        """Handle chat message from group"""
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'timestamp': timestamp
        }))

    async def typing_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
        }))

    async def user_online(self, event):
        """Handle user online notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_online',
            'username': event['username']
        }))

    async def user_offline(self, event):
        """Handle user offline notification"""
        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, message_text):
        """Save message to database"""
        other_user = CustomUser.objects.get(username=self.username)
        return Message.objects.create(
            sender=self.user,
            receiver=other_user,
            content=message_text
        )

    @database_sync_to_async
    def mark_user_online(self, user):
        """Mark user as online"""
        user.mark_online()

    @database_sync_to_async
    def mark_user_offline(self, user):
        """Mark user as offline"""
        user.mark_offline()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.room_group_name = f'notifications_{self.user.username}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def notification_message(self, event):
        """Handle notification message from group"""
        notification = event['notification']
        
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_type': notification['notification_type'],
            'title': notification['title'],
            'message': notification['message'],
            'timestamp': datetime.now().isoformat()
        }))


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for tracking online status"""
    
    async def connect(self):
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Broadcast user is online
        await self.channel_layer.group_add(
            'online_users',
            self.channel_name
        )
        
        await self.accept()
        
        # Notify all users that this user is online
        await self.channel_layer.group_send(
            'online_users',
            {
                'type': 'user_status_change',
                'username': self.user.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        # Notify all users that this user is offline
        await self.channel_layer.group_send(
            'online_users',
            {
                'type': 'user_status_change',
                'username': self.user.username,
                'status': 'offline'
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            'online_users',
            self.channel_name
        )

    async def user_status_change(self, event):
        """Handle user status change"""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'status': event['status']
        }))
