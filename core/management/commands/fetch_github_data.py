# core/management/commands/fetch_github_data.py
import requests

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from django.utils import timezone
from django.utils.timezone import make_aware

from core.models import Developer, Commit



# --- YOUR CONSTANTS ---

import os

# Ensure this token is secret in production environments!
# GITHUB_TOKEN must be set as an environment variable

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required. Please set it before running this command.")

GITHUB_ORG_OR_USER = 'eeshaanbharadwaj'

GITHUB_REPO_NAME = 'TeamPulse'

# ----------------------



class Command(BaseCommand):

    help = 'Fetches real commit data from GitHub API and updates the database.'



    def handle(self, *args, **options):

        self.stdout.write("--- Starting GitHub Data Fetch ---")

        

        # Define the API endpoint URL

        API_URL = f"https://api.github.com/repos/{GITHUB_ORG_OR_USER}/{GITHUB_REPO_NAME}/commits"

        

        # Headers for authentication and to accept JSON

        headers = {

            'Authorization': f'token {GITHUB_TOKEN}',

            'Accept': 'application/vnd.github.v3+json',

        }

        

        # Parameters to filter results (e.g., fetch commits from the last 30 days)

        since_date = (timezone.now() - timedelta(days=30)).isoformat()

        params = {

            'since': since_date,

            'per_page': 100 # Fetch up to 100 commits per page

        }



        try:

            response = requests.get(API_URL, headers=headers, params=params)

            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            commits_data = response.json()

            

            self.stdout.write(f"Fetched {len(commits_data)} commits from GitHub.")



            for commit_data in commits_data:

                # Skip commits without author info (e.g., if force-pushed)

                if not commit_data.get('author') or not commit_data['commit'].get('author'):

                    continue

                

                # --- 1. Get or Create Developer ---

                author_email = commit_data['commit']['author']['email']

                author_name = commit_data['commit']['author']['name']

                

                # We use email as the unique identifier for Developer

                developer, created = Developer.objects.get_or_create(

                    email=author_email,

                    defaults={'name': author_name}

                )

                if created:

                    self.stdout.write(self.style.SUCCESS(f"Created new developer: {author_name}"))



                # --- 2. Create Commit Record ---

                commit_hash = commit_data['sha']

                

                # Check if commit already exists (using hash_id as unique key)

                if Commit.objects.filter(hash_id=commit_hash).exists():

                    # self.stdout.write(f"Commit {commit_hash[:7]} already exists. Skipping.")

                    continue



                commit_timestamp_str = commit_data['commit']['author']['date']

                commit_timestamp = datetime.strptime(commit_timestamp_str, '%Y-%m-%dT%H:%M:%SZ')

                

                # NOTE: GitHub API doesn't easily give lines_added/removed in this endpoint.

                # A proper implementation would require a SECOND API call per commit to get stats, 

                # but we will simplify for now by using dummy data for stats.

                lines_added = commit_data.get('stats', {}).get('additions', 50) # Use a dummy value if stats not present

                lines_removed = commit_data.get('stats', {}).get('deletions', 20) # Use a dummy value

                

                Commit.objects.create(

                    developer=developer,

                    hash_id=commit_hash,

                    message=commit_data['commit']['message'][:500], # Truncate message

                    lines_added=lines_added,

                    lines_removed=lines_removed,

                    timestamp=make_aware(commit_timestamp),

                    is_merge="Merge pull request" in commit_data['commit']['message']

                )

                self.stdout.write(f"  > Saved commit {commit_hash[:7]}")




            self.stdout.write(self.style.SUCCESS("\nGitHub Data Fetch Complete."))



        except requests.exceptions.RequestException as e:

            self.stdout.write(self.style.ERROR(f"\nAPI Request Failed: {e}"))

            self.stdout.write(self.style.ERROR("Check your GITHUB_TOKEN and ensure the repo exists."))


