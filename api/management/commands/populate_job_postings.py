from django.core.management.base import BaseCommand
from django.core.management import call_command
from api.models import JobPosting
from collections import defaultdict
import json
import os

class Command(BaseCommand):
    help = 'Check and populate job postings data from fixtures'

    def load_fixture_data(self):
        """Load and parse the fixture file."""
        fixture_path = os.path.join('api', 'fixtures', 'job_postings.json')
        try:
            with open(fixture_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading fixture file: {str(e)}'))
            return None

    def handle(self, *args, **kwargs):
        # Load fixture data
        fixture_data = self.load_fixture_data()
        if not fixture_data:
            return

        # Get existing jobs
        existing_jobs = JobPosting.objects.all()
        existing_titles = {job.title: job for job in existing_jobs}
        
        # Track which jobs from fixtures are already in the database
        jobs_to_add = []
        jobs_already_exist = []
        
        # Check each job from fixtures
        for job_data in fixture_data:
            title = job_data['fields']['title']
            if title in existing_titles:
                jobs_already_exist.append(existing_titles[title])
            else:
                jobs_to_add.append(job_data)

        # Display existing jobs
        if existing_jobs.exists():
            self.stdout.write(self.style.SUCCESS('Existing job postings in database:'))
            for job in existing_jobs:
                self.stdout.write(f'\n- Title: {job.title}')
                self.stdout.write(f'  Company: {job.company}')
                self.stdout.write(f'  Required Skills: {", ".join(job.required_skills)}')
                self.stdout.write(f'  ID: {job.id}')

        # Display jobs that match fixtures
        if jobs_already_exist:
            self.stdout.write(self.style.WARNING('\nJobs from fixtures that already exist:'))
            for job in jobs_already_exist:
                self.stdout.write(f'\n- Title: {job.title}')
                self.stdout.write(f'  Company: {job.company}')
                self.stdout.write(f'  Required Skills: {", ".join(job.required_skills)}')
                self.stdout.write(f'  ID: {job.id}')

        # Add missing jobs
        if jobs_to_add:
            self.stdout.write(self.style.WARNING('\nAdding missing jobs from fixtures...'))
            try:
                # Create a temporary fixture file with only missing jobs
                temp_fixture_path = os.path.join('api', 'fixtures', 'temp_job_postings.json')
                with open(temp_fixture_path, 'w') as f:
                    json.dump(jobs_to_add, f)
                
                # Load only the missing jobs
                call_command('loaddata', 'temp_job_postings', verbosity=0)
                
                # Clean up temporary file
                os.remove(temp_fixture_path)
                
                # Display newly added jobs
                self.stdout.write(self.style.SUCCESS('\nSuccessfully added new job postings:'))
                for job_data in jobs_to_add:
                    title = job_data['fields']['title']
                    company = job_data['fields']['company']
                    skills = job_data['fields']['required_skills']
                    self.stdout.write(f'\n- Title: {title}')
                    self.stdout.write(f'  Company: {company}')
                    self.stdout.write(f'  Required Skills: {", ".join(skills)}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error adding new job postings: {str(e)}'))
        else:
            self.stdout.write(self.style.SUCCESS('\nNo new jobs to add from fixtures.')) 