import json
import pdfplumber
import docx
import os
from .models import CandidateProfile, JobPosting, JobMatch
from .llm_client import call_llm

def extract_text_from_pdf(file_path):
    """Extracts text from PDF files using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = []
            for page in pdf.pages:
                text.append(page.extract_text() or "")
            return "\n".join(text)
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_doc(file_path):
    """Extracts text from DOC/DOCX files."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Error extracting text from DOC/DOCX: {str(e)}")

def extract_text_from_resume(file_path):
    """Extracts text from resume files (PDF or DOC/DOCX)."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension in ['.doc', '.docx']:
        return extract_text_from_doc(file_path)
    else:
        raise ValueError("Unsupported file format")

def parse_resume(file_path):
    """Calls LLM to extract structured data from resume text."""
    try:
        # Extract text from the resume
        text = extract_text_from_resume(file_path)
        
        if not text.strip():
            raise ValueError("No text could be extracted from the resume")
        
        # Call LLM to extract structured data
        response = call_llm(
            "Extract the following information from the resume text: name, email, phone, skills, experience, education. "
            "Format the response as a JSON object with these fields.",
            "parse_resume",
            {"resume_text": text}
        )
        
        parsed_data = json.loads(response)
        
        # Validate required fields
        required_fields = ['name', 'email']
        missing_fields = [field for field in required_fields if field not in parsed_data]
        if missing_fields:
            raise ValueError(f"Missing required fields in parsed data: {', '.join(missing_fields)}")
            
        return parsed_data
        
    except Exception as e:
        raise Exception(f"Error parsing resume: {str(e)}")

def parse_job_posting(job_text):
    """Calls LLM to extract structured job data."""
    response = call_llm(
        "Extract structured job details from the posting.",
        "parse_job_posting",
        {"job_text": job_text}
    )
    return json.loads(response)

def match_candidate_to_job(candidate, job):
    """Calls LLM to match a candidate with a job."""
    response = call_llm(
        "Evaluate job match for the candidate.",
        "match_candidate_to_job",
        {
            "candidate_data": candidate,
            "job_data": job
        }
    )
    return json.loads(response)

def generate_cover_letter(candidate, job):
    """Calls LLM to generate a cover letter."""
    response = call_llm(
        "Generate a personalized cover letter.",
        "generate_cover_letter",
        {
            "candidate_data": candidate,
            "job_data": job
        }
    )
    return json.loads(response)["cover_letter"]
