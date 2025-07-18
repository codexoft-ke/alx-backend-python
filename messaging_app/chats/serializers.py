from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User, Conversation, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'phone_number',
            'role',
            'created_at',
            'is_active',
            'is_staff'
        ]
        read_only_fields = ['user_id', 'created_at', 'is_staff']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password
        """
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
    def update(self, instance, validated_data):
        """
        Update user instance, handling password encryption
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified User serializer for nested relationships
    """
    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role'
        ]
        read_only_fields = ['user_id']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSimpleSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_id',
            'conversation',
            'message_body',
            'sent_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Create a new message
        """
        sender_id = validated_data.pop('sender_id')
        sender = User.objects.get(user_id=sender_id)
        validated_data['sender'] = sender
        return super().create(validated_data)


class MessageSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified Message serializer for nested relationships
    """
    sender = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages
    """
    participants = UserSimpleSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSimpleSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'last_message',
            'message_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation
        """
        last_message = obj.get_last_message()
        if last_message:
            return MessageSimpleSerializer(last_message).data
        return None
    
    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()
    
    def create(self, validated_data):
        """
        Create a new conversation with participants
        """
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation
    
    def update(self, instance, validated_data):
        """
        Update conversation, handling participants
        """
        participant_ids = validated_data.pop('participant_ids', None)
        conversation = super().update(instance, validated_data)
        
        if participant_ids is not None:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        return conversation


class ConversationSimpleSerializer(serializers.ModelSerializer):
    """
    Simplified Conversation serializer for nested relationships
    """
    participants = UserSimpleSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'last_message',
            'message_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        """
        Get the most recent message in the conversation
        """
        last_message = obj.get_last_message()
        if last_message:
            return {
                'message_id': last_message.message_id,
                'message_body': last_message.message_body[:50] + '...' if len(last_message.message_body) > 50 else last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender': last_message.sender.username
            }
        return None
    
    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Detailed Conversation serializer with full message history
    """
    participants = UserSimpleSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
            'message_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']
    
    def get_messages(self, obj):
        """
        Get all messages in the conversation, ordered by sent_at
        """
        messages = obj.messages.all().order_by('sent_at')
        return MessageSimpleSerializer(messages, many=True).data
    
    def get_message_count(self, obj):
        """
        Get the total number of messages in the conversation
        """
        return obj.messages.count()


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating messages
    """
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body'
        ]
        read_only_fields = ['message_id']
    
    def validate_conversation(self, value):
        """
        Validate that the sender is a participant in the conversation
        """
        user = self.context['request'].user
        if not value.participants.filter(user_id=user.user_id).exists():
            raise serializers.ValidationError(
                "You are not a participant in this conversation."
            )
        return value
