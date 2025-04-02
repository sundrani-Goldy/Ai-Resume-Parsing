from rest_framework import serializers
from .models import CandidateProfile, JobPosting, JobMatch,CoverLetter
from api.services import parse_job_posting

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = "__all__"

class ResumeUploadSerializer(serializers.Serializer):
    resume_file = serializers.FileField(required=True)

class JobPostingSerializer(serializers.ModelSerializer):
    job_text = serializers.CharField(write_only=True)  # Add job_text as a write-only field

    class Meta:
        model = JobPosting
        fields = "__all__"  # Use all fields of the JobPosting model including job_text

    def create(self, validated_data):
        """Override create method to handle unstructured job text parsing."""
        job_text = validated_data.pop('job_text', None)  # Extract raw job text from the input
        
        if job_text:
            # Parse the unstructured job text using the LLM
            parsed_data = parse_job_posting(job_text)
            
            # Create a JobPosting instance using parsed data
            job_posting = JobPosting.objects.create(
                title=parsed_data.get("title"),
                company=parsed_data.get("company"),
                required_skills=parsed_data.get("required_skills"),
                description=parsed_data.get("description")
            )
            return job_posting
        else:
            # If no job_text is provided, proceed with the standard create method
            return super().create(validated_data)


class JobMatchSerializer(serializers.ModelSerializer):
    candidate = CandidateProfileSerializer()
    job = JobPostingSerializer()

    class Meta:
        model = JobMatch
        fields = "__all__"

class CoverLetterSerializer(serializers.ModelSerializer):
    candidate_id = serializers.PrimaryKeyRelatedField(queryset=CandidateProfile.objects.all(), source='candidate')
    job_id = serializers.PrimaryKeyRelatedField(queryset=JobPosting.objects.all(), source='job')

    class Meta:
        model = CoverLetter
        fields = ["id", "candidate_id", "job_id", "content", "created_at", "updated_at"]