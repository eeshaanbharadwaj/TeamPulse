# core/models.py
from django.db import models

class Developer(models.Model):
    """A model to represent a developer."""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # We'll add a link to a 'Team' model later

    def __str__(self):
        return self.name

class Commit(models.Model):
    """A model to store a code commit."""
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    hash_id = models.CharField(max_length=40, unique=True)
    message = models.TextField()
    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

    # Simple flags for ML feature engineering later
    is_merge = models.BooleanField(default=False) 

    # Link to Jira ticket
    ticket = models.ForeignKey('JiraTicket', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Commit {self.hash_id[:7]} by {self.developer.name}"


class JiraTicket(models.Model):
    """A model to represent a Jira/project management ticket."""
    ticket_key = models.CharField(max_length=20, unique=True)  # e.g., TEAM-123
    title = models.CharField(max_length=255)
    assignee = models.ForeignKey(
        'Developer', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_tickets'
    )
    status = models.CharField(max_length=50)  # e.g., 'To Do', 'In Progress', 'Done'
    story_points = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Track the time spent actively working on it (for burnout/load)
    time_spent_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.ticket_key}: {self.title}"


class ChatData(models.Model):
    """A model to store team communication data (e.g., from Slack/Teams)."""
    sender = models.ForeignKey(
        'Developer', 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        'Developer', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='received_messages',
        help_text="Null for channel messages."
    )
    timestamp = models.DateTimeField()
    # Length of the message (a simple proxy for communication style)
    message_length = models.IntegerField(default=0)
    
    # Key ML features for sentiment and communication analysis
    sentiment_score = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # A simple indicator of whether the message was a quick reply
    is_quick_response = models.BooleanField(default=False) 

    def __str__(self):
        return f"Chat from {self.sender.name} at {self.timestamp.time()}"