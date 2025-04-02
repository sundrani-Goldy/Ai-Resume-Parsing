from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
import os
from django.core.files.storage import default_storage
from api.models import CandidateProfile, JobPosting, JobMatch
from api.serializers import *
from api.services import parse_resume, match_candidate_to_job, generate_cover_letter, parse_job_posting
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CandidateProfileViewSet(ViewSet):
    queryset = CandidateProfile.objects.all()
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload a resume file to create a candidate profile",
        manual_parameters=[
            openapi.Parameter(
                'resume_file',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='Resume file in PDF or DOCX format'
            )
        ],
        responses={
            201: openapi.Response(
                description="Candidate profile created successfully",
                examples={
                    "application/json": {
                        "name": "John Doe",
                        "email": "john.doe@example.com",
                        "phone": "123-456-7890",
                        "skills": ["Python", "Django"],
                        "education": [],
                        "work_experience": [],
                        "resume_file": "resumes/john_doe_resume.pdf"
                    }
                }
            ),
            400: 'Bad Request'
        }
    )
    @action(detail=False, methods=["post"])
    def upload_resume(self, request):
        upload_serializer = ResumeUploadSerializer(data=request.data)
        
        if not upload_serializer.is_valid():
            return Response(upload_serializer.errors, status=400)
            
        file = request.FILES["resume_file"]
        
        # Save the file first
        path = default_storage.save(f"resumes/{file.name}", file)
        
        try:
            # Get absolute path to the file for parsing
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            
            # Parse the resume
            parsed_data = parse_resume(full_path)
            
            # Create the candidate profile
            candidate = CandidateProfile(
                name=parsed_data.get('name', ''),
                email=parsed_data.get('email', ''),
                phone=parsed_data.get('phone', ''),
                skills=parsed_data.get('skills', []),
                education=parsed_data.get('education', []),
                work_experience=parsed_data.get('work_experience', []),
                resume_file=path
                # Remove created_at - it will be automatically set
            )
            candidate.save()
            
            return Response(CandidateProfileSerializer(candidate).data, status=201)
        except Exception as e:
            # Clean up the file if parsing fails
            default_storage.delete(path)
            return Response({"error": str(e)}, status=400)

class JobPostingViewSet(ViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer

    def get_serializer(self, *args, **kwargs):
        """Manually provide a serializer instance, as ViewSet lacks get_serializer"""
        return self.serializer_class(*args, **kwargs)

    @swagger_auto_schema(
        operation_description="List all job postings",
        responses={
            200: openapi.Response(
                description="List of job postings",
                examples={
                    "application/json": {
                        "count": 2,
                        "results": [
                            {
                                "id": 1,
                                "title": "Software Engineer",
                                "company": "Tech Corp",
                                "required_skills": ["Python", "Django", "React"],
                                "description": "Looking for an experienced software engineer..."
                            },
                            {
                                "id": 2,
                                "title": "Data Scientist",
                                "company": "Data Corp",
                                "required_skills": ["Python", "Machine Learning", "SQL"],
                                "description": "Seeking a skilled data scientist..."
                            }
                        ]
                    }
                }
            )
        }
    )
    def list(self, request):
        """List all job postings."""
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "job_text": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Raw, unstructured job posting text to be parsed into structured data."
            )
        },
        required=["job_text"],
    )
    )
    @action(detail=False, methods=['post'])
    def create_from_text(self, request, *args, **kwargs):
        """Accept unstructured job posting text and parse it with LLM."""
        
        job_text = request.data.get("job_text", "").strip()

        if not job_text:
            return Response({"error": "Job text is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Pass unstructured job text to LLM for parsing
            structured_data = parse_job_posting(job_text)  # Call LLM function here
            
            # Ensure structured_data contains required fields
            job_posting = JobPosting.objects.create(
                title=structured_data.get("title", "Untitled"),
                company=structured_data.get("company", "Unknown"),
                required_skills=structured_data.get("required_skills", []),
                description=structured_data.get("description", job_text)
            )

            return Response(JobPostingSerializer(job_posting).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobMatchViewSet(ViewSet):
    queryset = JobMatch.objects.all()
    serializer_class = JobMatchSerializer

    @swagger_auto_schema(
        operation_description="Match a candidate with a job posting",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'candidate_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the candidate'),
                'job_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the job posting'),
            },
        ),
        responses={200: JobMatchSerializer, 404: 'Not Found'}
    )
    @action(detail=False, methods=["post"])
    def match(self, request):
        try:
            candidate = CandidateProfile.objects.get(id=request.data["candidate_id"])
            job = JobPosting.objects.get(id=request.data["job_id"])

            # Serialize data before sending to LLM
            candidate_data = CandidateProfileSerializer(candidate).data
            job_data = JobPostingSerializer(job).data

            # Call LLM
            match_data = match_candidate_to_job(candidate_data, job_data)

            match = JobMatch.objects.create(candidate=candidate, job=job, **match_data)
            return Response(JobMatchSerializer(match).data, status=status.HTTP_201_CREATED)
        
        except CandidateProfile.DoesNotExist:
            return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job posting not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CoverLetterViewSet(ViewSet):
    queryset = CoverLetter.objects.all()
    serializer_class = CoverLetterSerializer

    @swagger_auto_schema(
        operation_description="Generate a cover letter for a candidate and job",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'candidate_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the candidate'),
                'job_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the job posting'),
            },
            required=['candidate_id', 'job_id']
        ),
        responses={
            200: openapi.Response(
                description="Generated cover letter",
                examples={
                    "application/json": {
                        "id": 1,
                        "candidate_id": 2,
                        "job_id": 3,
                        "content": "Dear Hiring Manager, I am writing to express my interest in...",
                        "created_at": "2025-04-02T12:00:00Z",
                        "updated_at": "2025-04-02T12:00:00Z"
                    }
                }
            ),
            404: 'Not Found'
        }
    )
    @action(detail=False, methods=["post"])
    def generate_cover_letter(self, request):
        try:
            candidate_id = request.data.get('candidate_id')
            job_id = request.data.get('job_id')

            if not candidate_id or not job_id:
                return Response(
                    {"error": "Both candidate_id and job_id are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get candidate and job objects
            candidate = CandidateProfile.objects.get(id=candidate_id)
            job = JobPosting.objects.get(id=job_id)

            # Serialize the data before sending to LLM
            candidate_data = CandidateProfileSerializer(candidate).data
            job_data = JobPostingSerializer(job).data

            # Generate cover letter using LLM with serialized data
            cover_letter_text = generate_cover_letter(
                candidate_data,
                job_data
            )

            # Create and save the cover letter
            cover_letter = CoverLetter.objects.create(
                candidate=candidate,
                job=job,
                content=cover_letter_text
            )

            return Response(
                CoverLetterSerializer(cover_letter).data,
                status=status.HTTP_201_CREATED
            )

        except CandidateProfile.DoesNotExist:
            return Response(
                {"error": "Candidate not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except JobPosting.DoesNotExist:
            return Response(
                {"error": "Job posting not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

