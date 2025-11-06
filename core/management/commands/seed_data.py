# core/management/commands/seed_data.py
import random
from datetime import timedelta, datetime
from django.core.management.base import BaseCommand
from core.models import Developer, Commit, JiraTicket, ChatData
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with sample data for TeamPulse analysis.'

    def handle(self, *args, **options):
        self.stdout.write("--- Starting Data Seeding ---")
        
        # 1. Clear existing data (optional, but good for clean tests)
        Developer.objects.all().delete()
        Commit.objects.all().delete()
        JiraTicket.objects.all().delete()
        ChatData.objects.all().delete()
        self.stdout.write(self.style.WARNING("Existing data cleared."))

        # --- 2. Create Developers ---
        dev_names = ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Eve Davis', 'Dave Lee']
        developers = []
        for name in dev_names:
            dev = Developer.objects.create(
                name=name, 
                email=f"{name.replace(' ', '.').lower()}@teampulse.com"
            )
            developers.append(dev)
        self.stdout.write(self.style.SUCCESS(f"Created {len(developers)} Developers."))

        # --- 3. Generate Commits (Simulating 30 days of activity) ---
        today = timezone.now()
        commit_count = 0
        
        for dev in developers:
            for day in range(30):
                # Simulate more work on weekdays, less on weekends
                num_commits = random.randint(2, 8) if datetime.now().weekday() < 5 else random.randint(0, 3) 
                
                for _ in range(num_commits):
                    # Random time of day, some commits will be late at night (Burnout feature!)
                    time_offset = timedelta(hours=random.randint(9, 23), minutes=random.randint(0, 59))
                    commit_time = today - timedelta(days=day) - time_offset
                    
                    Commit.objects.create(
                        developer=dev,
                        hash_id=f'{random.getrandbits(32):08x}',
                        message=f"Feature: Added login functionality. ({_})",
                        lines_added=random.randint(10, 200),
                        lines_removed=random.randint(5, 100),
                        timestamp=commit_time,
                        is_merge=random.random() < 0.1 # 10% are merge commits
                    )
                    commit_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {commit_count} Sample Commits."))

        # --- 4. Generate Jira Tickets ---
        ticket_count = 0
        for i in range(50):
            status = random.choice(['Done', 'In Progress', 'To Do', 'Review'])
            assignee = random.choice(developers)
            created = today - timedelta(days=random.randint(5, 60))
            closed = created + timedelta(days=random.randint(1, 15)) if status == 'Done' else None
            
            JiraTicket.objects.create(
                ticket_key=f"PROD-{100 + i}",
                title=f"Bug fix for component {i}",
                assignee=assignee,
                status=status,
                story_points=random.choice([1, 2, 3, 5, 8]),
                created_at=created,
                closed_at=closed,
                time_spent_hours=random.uniform(2.0, 40.0)
            )
            ticket_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {ticket_count} Sample Jira Tickets."))

        # --- 5. Generate Chat Data ---
        chat_count = 0
        for i in range(200): # Create 200 random chat messages
            sender = random.choice(developers)
            
            # 70% of messages are channel messages (recipient=None)
            if random.random() < 0.7:
                recipient = None
            else:
                # 30% are direct messages, must be to a different person
                recipient = random.choice([d for d in developers if d != sender])

            chat_time = today - timedelta(days=random.randint(1, 30), hours=random.randint(9, 23))

            # Simulate ML Features
            
            # Sentiment Score: Randomly assign a positive, neutral, or negative score
            sentiment_score = random.uniform(0.1, 0.99) # Score between 0.1 and 0.99
            
            # Quick Response: Simulate 60% of messages being quick responses
            is_quick_response = random.random() < 0.6 
            
            ChatData.objects.create(
                sender=sender,
                recipient=recipient,
                timestamp=chat_time,
                message_length=random.randint(5, 50),
                sentiment_score=sentiment_score, # <-- NEW
                is_quick_response=is_quick_response, # <-- NEW
            )
            chat_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {chat_count} Sample Chat Messages."))

        self.stdout.write("--- Data Seeding Complete ---")