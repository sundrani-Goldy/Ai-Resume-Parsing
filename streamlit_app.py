import streamlit as st
import requests
import json

# Set page config
st.set_page_config(
    page_title="AI Resume Parser & Job Matcher",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    .main {
        padding: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Upload Resume", "Add Job Posting", "Match Jobs"]
)

# API base URL
API_BASE_URL = "http://localhost:8000/api"

def upload_resume_page():
    st.title("📄 Upload Resume")
    st.write("Upload your resume to be parsed and matched with jobs")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a resume file", type=["pdf", "docx"])
    
    if uploaded_file:
        
        if st.button("Upload and Parse Resume"):
            with st.spinner("Parsing resume..."):
                files = {"resume_file": uploaded_file}
                
                try:
                    response = requests.post(f"{API_BASE_URL}/candidates/upload_resume/", files=files)

                    if response.status_code in [200, 201]:
                        try:
                            data = response.json()
                        except ValueError:
                            st.error(f"Unexpected response format: {response.text}")
                            return
                        
                        st.success("✅ Resume uploaded and parsed successfully!")

                        # Tabs for displaying parsed data
                        tab1, tab2, tab3 = st.tabs(["Personal Info", "Skills", "Experience & Education"])

                        with tab1:
                            st.subheader("Personal Information")
                            st.write(f"**Name:** {data.get('name', 'N/A')}")
                            st.write(f"**Email:** {data.get('email', 'N/A')}")
                            if data.get('phone'):
                                st.write(f"**Phone:** {data.get('phone', 'N/A')}")

                        with tab2:
                            st.subheader("Skills")
                            skills = data.get('skills', [])
                            if skills:
                                st.write(", ".join(skills))
                            else:
                                st.info("No skills extracted")

                        with tab3:
                            st.subheader("Education")
                            education = data.get('education', [])
                            if education:
                                for edu in education:
                                    st.write(f"• {edu.get('degree', 'Degree')} - {edu.get('institution', 'Institution')} ({edu.get('year', '')})")
                            else:
                                st.info("No education information extracted")

                            st.subheader("Work Experience")
                            experience = data.get('work_experience', [])
                            if experience:
                                for exp in experience:
                                    st.write(f"• **{exp.get('title', 'Role')}** at {exp.get('company', 'Company')} ({exp.get('duration', '')})")
                                    if exp.get('description'):
                                        st.write(f"  {exp['description']}")
                            else:
                                st.info("No work experience extracted")

                    else:
                        # Extract error message from API response
                        error_msg = "Unknown error"
                        try:
                            error_data = response.json()
                            error_msg = error_data.get('error', error_msg)
                        except:
                            error_msg = response.text or str(response)
                        
                        st.error(f"❌ Error: {error_msg}")

                except requests.exceptions.RequestException as e:
                    st.error(f"🚨 Error connecting to server: {str(e)}")


def add_job_page():
    st.title("💼 Job Postings")
    
    # Section 1: List All Jobs
    st.subheader("Available Job Postings")
    
    with st.spinner("Loading job postings..."):
        try:
            # Fetch all jobs from the API
            response = requests.get(f"{API_BASE_URL}/jobs/")
            
            if response.status_code == 200:
                jobs = response.json()
                
                if jobs and len(jobs) > 0:
                    # Create a table/list of jobs
                    for job in jobs:
                        with st.expander(f"{job.get('title', 'Untitled')} at {job.get('company', 'Unknown Company')} (ID: {job.get('id')})"):
                            # Display job details
                            st.write(f"**Title:** {job.get('title', 'N/A')}")
                            st.write(f"**Company:** {job.get('company', 'N/A')}")
                            
                            # Display required skills as a bulleted list
                            st.write("**Required Skills:**")
                            skills = job.get('required_skills', [])
                            if skills:
                                for skill in skills:
                                    st.write(f"• {skill}")
                            else:
                                st.write("No specific skills listed")
                            
                            # Display job description
                            st.write("**Description:**")
                            st.write(job.get('description', 'No description available'))
                else:
                    st.info("No job postings available yet. Add one below!")
            else:
                st.error(f"⚠️ Could not load job postings. Status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"🚨 Error connecting to server: {str(e)}")
    
    # Add a separator between sections
    st.markdown("---")
    
    # Section 2: Create New Job Posting
    st.subheader("Add a New Job Posting")
    st.write("Paste a job description below to extract job details automatically")
    
    with st.form("job_posting_form"):
        job_text = st.text_area("Paste the Job Posting Text Here")
        
        submitted = st.form_submit_button("Add Job Posting")
        
        if submitted:
            if not job_text.strip():
                st.error("Job text cannot be empty.")
                return
            
            # Prepare JSON payload
            job_data = {"job_text": job_text}
            
            try:
                headers = {"Content-Type": "application/json"}
                response = requests.post(f"{API_BASE_URL}/jobs/create_from_text/", json=job_data, headers=headers)
                
                if response.status_code == 201:
                    data = response.json()
                    st.success("✅ Job posting added successfully!")
                    
                    # Tabs for displaying parsed data
                    tab1, tab2, tab3 = st.tabs(["Job Details", "Requirements", "Company Info"])
                    
                    with tab1:
                        st.subheader("Job Title")
                        st.write(f"**Title:** {data.get('title', 'N/A')}")
                        st.write(f"**Description:** {data.get('description', 'N/A')}")
                    
                    with tab2:
                        st.subheader("Requirements")
                        skills = data.get('required_skills', [])
                        if skills:
                            for skill in skills:
                                st.write(f"• {skill}")
                        else:
                            st.info("No specific skills extracted")
                    
                    with tab3:
                        st.subheader("Company Information")
                        st.write(f"**Company Name:** {data.get('company', 'N/A')}")
                        if data.get('location'):
                            st.write(f"**Location:** {data.get('location', 'N/A')}")
                    
                    # Refresh the page after a short delay to show the updated job list
                    import time
                    time.sleep(1)
                    st.rerun()
                        
                else:
                    error_msg = "Unknown error"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('error', error_msg)
                    except:
                        error_msg = response.text or str(response)
                    
                    st.error(f"❌ Error: {error_msg}")

            except requests.exceptions.RequestException as e:
                st.error(f"🚨 Error connecting to server: {str(e)}")


def match_jobs_page(): 
    st.title("🤝 Match Jobs")
    st.write("Match candidates with job postings")
    
    # Create a session state to track if we've already matched and if we should generate a cover letter
    if 'match_completed' not in st.session_state:
        st.session_state.match_completed = False
    
    if 'generate_cover_letter' not in st.session_state:
        st.session_state.generate_cover_letter = False
    
    if 'match_data' not in st.session_state:
        st.session_state.match_data = None
    
    # Input fields for Candidate ID and Job ID - only show if we haven't matched yet
    if not st.session_state.match_completed:
        candidate_id = st.number_input("Enter Candidate ID", min_value=1, step=1)
        job_id = st.number_input("Enter Job ID", min_value=1, step=1)
        
        if st.button("Match Candidate with Job"):
            with st.spinner("Matching..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/matches/match/",
                        json={"candidate_id": candidate_id, "job_id": job_id}
                    )
                    
                    # Try to parse the response as JSON regardless of status code
                    try:
                        match_data = response.json()
                        st.session_state.match_data = match_data
                        st.session_state.match_completed = True
                        # Force a rerun to show the results
                        st.rerun()
                        
                    except ValueError:
                        # If JSON parsing fails, show the raw response text
                        st.error(f"❌ Error: Unable to parse response data. Raw response: {response.text}")
                
                except Exception as e:
                    st.error(f"🚨 Error connecting to server: {str(e)}")
    
    # If we've completed a match, show the results
    if st.session_state.match_completed and st.session_state.match_data:
        match_data = st.session_state.match_data
        
        # Add a reset button at the top
        if st.button("Start New Match", key="reset_match"):
            st.session_state.match_completed = False
            st.session_state.generate_cover_letter = False
            st.session_state.match_data = None
            st.rerun()
            return
            
        st.success("✅ Match data retrieved successfully!")
        
        # Creating tabs
        tab1, tab2, tab3, tab4 = st.tabs(["👤 Candidate Info", "💼 Job Details", "📊 Match Summary", "📝 Cover Letter"])
        
        with tab1:
            st.subheader("Candidate Information")
            st.write(f"**Name:** {match_data['candidate']['name']}")
            st.write(f"**Email:** {match_data['candidate']['email']}")
            st.write(f"**Phone:** {match_data['candidate']['phone']}")
            st.write("**Skills:**")
            st.write(", ".join(match_data['candidate']['skills']) if match_data['candidate']['skills'] else "No skills listed")
            
            # Display education if available
            if 'education' in match_data['candidate'] and match_data['candidate']['education']:
                st.write("**Education:**")
                for edu in match_data['candidate']['education']:
                    st.write(f"- {edu['year']}: {edu['degree']} from {edu['institution']}")
            
            # Display work experience if available
            if 'work_experience' in match_data['candidate'] and match_data['candidate']['work_experience']:
                st.write("**Work Experience:**")
                for exp in match_data['candidate']['work_experience']:
                    st.write(f"- **{exp['title']}** at {exp['company']} ({exp['duration']})")
                    st.write(f"  {exp['description']}")
        
        with tab2:
            st.subheader("Job Details")
            st.write(f"**Title:** {match_data['job']['title']}")
            st.write(f"**Company:** {match_data['job']['company']}")
            st.write("**Required Skills:**")
            for skill in match_data['job']['required_skills']:
                st.write(f"- {skill}")
            st.write("**Job Description:**")
            st.write(match_data['job']['description'])

        with tab3:
            st.subheader("Match Results")
            st.write(f"**Match Score:** {match_data['match_score']}%")
            st.write("**Missing Skills:**")
            for skill in match_data['missing_skills']:
                st.write(f"- {skill}")
            st.write("**Summary:**")
            st.write(match_data['summary'])
        
        with tab4:
            st.subheader("Cover Letter")
            candidate_id = match_data['candidate']['id']
            job_id = match_data['job']['id']
            
            # Check if we've already generated a cover letter or if the button was clicked
            if not st.session_state.generate_cover_letter:
                if st.button("Generate Cover Letter", key="generate_cover_letter_button"):
                    st.session_state.generate_cover_letter = True
                    st.rerun()
            
            # If we should generate a cover letter, do so
            if st.session_state.generate_cover_letter:
                with st.spinner("Generating cover letter..."):
                    try:
                        cover_letter_response = requests.post(
                            f"{API_BASE_URL}/coverletters/generate_cover_letter/",
                            json={"candidate_id": candidate_id, "job_id": job_id}
                        )
                        
                        if cover_letter_response.status_code in [200, 201]:
                            try:
                                cover_letter_data = cover_letter_response.json()
                                
                                # Display the cover letter in a nice format
                                st.markdown("### Generated Cover Letter")
                                st.markdown("---")
                                
                                # Check the structure of the response and display accordingly
                                if isinstance(cover_letter_data, dict) and "content" in cover_letter_data:
                                    st.markdown(cover_letter_data["content"])
                                    cover_letter_text = cover_letter_data["content"]
                                else:
                                    # Handle both string and dict responses
                                    if isinstance(cover_letter_data, str):
                                        st.markdown(cover_letter_data)
                                        cover_letter_text = cover_letter_data
                                    else:
                                        st.markdown(str(cover_letter_data))
                                        cover_letter_text = str(cover_letter_data)
                                
                                # Add download button for the cover letter
                                st.download_button(
                                    label="Download Cover Letter",
                                    data=cover_letter_text,
                                    file_name=f"cover_letter_{match_data['candidate']['name']}_{match_data['job']['title']}.txt",
                                    mime="text/plain"
                                )
                            except ValueError:
                                # Response is not JSON
                                st.markdown("### Generated Cover Letter")
                                st.markdown("---")
                                cover_letter_text = cover_letter_response.text
                                st.markdown(cover_letter_text)
                                
                                st.download_button(
                                    label="Download Cover Letter",
                                    data=cover_letter_text,
                                    file_name=f"cover_letter_{match_data['candidate']['name']}_{match_data['job']['title']}.txt",
                                    mime="text/plain"
                                )
                        else:
                            st.error(f"❌ Error generating cover letter: {cover_letter_response.text}")
                    
                    except Exception as e:
                        st.error(f"🚨 Error connecting to server: {str(e)}")
                
                # Add a button to regenerate the cover letter if needed
                if st.button("Regenerate Cover Letter", key="regenerate_cover_letter"):
                    st.rerun()

# Main content based on navigation
if page == "Upload Resume":
    upload_resume_page()
elif page == "Add Job Posting":
    add_job_page()
elif page == "Match Jobs":
    match_jobs_page()
