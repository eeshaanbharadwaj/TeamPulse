# core/serializers.py
from rest_framework import serializers
from .models import Developer, Commit, JiraTicket, ChatData

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ['id', 'name', 'email'] # Fields to expose in the API

class CommitSerializer(serializers.ModelSerializer):
    # Use the DeveloperSerializer to show the developer details, 
    # or use a PrimaryKeyRelatedField for simplicity. Let's use name for clarity.
    developer_name = serializers.ReadOnlyField(source='developer.name')

    class Meta:
        model = Commit
        fields = [
            'id', 
            'developer', 
            'developer_name', 
            'hash_id', 
            'message', 
            'lines_added', 
            'lines_removed', 
            'timestamp', 
            'is_merge'
        ]
        read_only_fields = ['developer_name'] # The user shouldn't set the name


class JiraTicketSerializer(serializers.ModelSerializer):
    assignee_name = serializers.ReadOnlyField(source='assignee.name')

    class Meta:
        model = JiraTicket
        fields = '__all__'


class ChatDataSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.name')

    class Meta:
        model = ChatData
        fields = '__all__'