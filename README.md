# AI Resume Parsing and Job Matching System

This application is a comprehensive solution for parsing resumes, matching candidates with job postings, and generating personalized cover letters using AI. It consists of a Django REST API backend and a Streamlit frontend.

## Features

- Resume parsing and candidate profile creation
- Job posting management
- AI-powered job matching
- Cover letter generation
- Interactive web interface

## Tech Stack

- Backend: Django REST Framework
- Frontend: Streamlit
- Database: PostgreSQL
- AI/ML: LLM Integration
- File Handling: PDF and DOCX support

## Project Structure

```
.
├── api/                    # Django app containing models and API endpoints
│   ├── fixtures/          # JSON fixtures for initial data
│   ├── management/        # Custom management commands
│   └── services/          # Business logic and AI services
├── core/                  # Django project settings
├── streamlit_app.py       # Streamlit frontend application
└── requirements.txt       # Python dependencies
```

## Setup and Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   ```

2. Navigate into the project directory
   ```bash
   cd <project-directory>
   ```

3. Start the application using Docker:
   ```bash
   docker-compose up --build
   ```

## Usage

1. Access the Streamlit interface at `http://localhost:8501`
2. Upload resumes through the interface
3. Add job postings using the job posting page
4. Match candidates with jobs
5. Generate cover letters for matches

## API Documentation

The API documentation is available at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`


## API Endpoints

### Candidate Profile Management

#### 1. Upload Resume
- **Endpoint**: `POST /api/candidates/upload_resume/`
- **Description**: Upload a resume file to create a candidate profile
- **Input**: 
  - `resume_file`: PDF or DOCX file
- **Output**: Created candidate profile with parsed information
- **Example Response**:
```json
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "123-456-7890",
    "skills": ["Python", "Django"],
    "education": [],
    "work_experience": [],
    "resume_file": "resumes/john_doe_resume.pdf"
}
```

### Job Posting Management

#### 1. List All Jobs
- **Endpoint**: `GET /api/jobs/`
- **Description**: Retrieve all job postings
- **Output**: List of all job postings
- **Example Response**:
```json
[
    {
        "id": 1,
        "title": "Python Developer",
        "company": "Tech Solutions Inc",
        "required_skills": ["Python", "Django", "REST APIs"],
        "description": "Job description..."
    }
]
```

#### 2. List All Jobs
- **Endpoint**: `GET /api/jobs/`
- **Description**: Retrieve all job postings
- **Output**: List of all job postings with structured data

### Job Matching

#### 1. Match Candidate with Job
- **Endpoint**: `POST /api/matches/match/`
- **Description**: Match a candidate with a job posting
- **Input**:
  - `candidate_id`: ID of the candidate
  - `job_id`: ID of the job posting
- **Output**: Match details including score and missing skills
- **Example Response**:
```json
{
    "candidate": {
        "name": "John Doe",
        "skills": ["Python", "Django"]
    },
    "job": {
        "title": "Python Developer",
        "required_skills": ["Python", "Django", "React"]
    },
    "match_score": 85,
    "missing_skills": ["React"],
    "summary": "Strong match with some missing skills..."
}
```

### Cover Letter Generation

#### 1. Generate Cover Letter
- **Endpoint**: `POST /api/coverletters/generate_cover_letter/`
- **Description**: Generate a personalized cover letter
- **Input**:
  - `candidate_id`: ID of the candidate
  - `job_id`: ID of the job posting
- **Output**: Generated cover letter
- **Example Response**:
```json
{
    "id": 1,
    "candidate_id": 2,
    "job_id": 3,
    "content": "Dear Hiring Manager...",
    "created_at": "2024-04-02T12:00:00Z",
    "updated_at": "2024-04-02T12:00:00Z"
}
```
All APIs are available on the Swagger UI for easy testing and exploration at [https://localhost:8000/swagger/](https://localhost:8000/swagger/).

## Streamlit Interface

The Streamlit interface provides an interactive way to use all the API features:

### Pages

1. **Upload Resume**
   - File upload interface for resumes
   - Displays parsed candidate information
   - Shows success/error messages

2. **Add Job Posting**
   - Text input for job description
   - Displays structured job data
   - Shows parsing results

3. **Match Jobs**
   - Input fields for candidate and job IDs
   - Displays match results in tabs:
     - Candidate Info
     - Job Details
     - Match Summary
   - Shows match score and missing skillst

## Database Models

### CandidateProfile
- Stores parsed resume information
- Fields: name, email, phone, skills, education, work_experience, resume_file

### JobPosting
- Stores job posting information
- Fields: title, company, required_skills, description

### JobMatch
- Links candidates with jobs
- Fields: candidate, job, match_score, missing_skills, summary

### CoverLetter
- Stores generated cover letters
- Fields: candidate, job, content, created_at, updated_at