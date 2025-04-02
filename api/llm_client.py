import os
import json
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def call_llm(system_prompt, function_name, arguments):
    """
    Call the OpenAI API with a function calling pattern using the v1.0.0+ client
    
    Args:
        system_prompt: Instructions for how to process the input
        function_name: The name of the function to call
        arguments: Dictionary of arguments to pass to the function
    
    Returns:
        The function call result as a string
    """
    # Define the function schema based on the function name
    function_schemas = {
        "parse_resume": {
            "name": "parse_resume",
            "description": "Extract structured information from resume text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full name of the candidate"},
                    "email": {"type": "string", "description": "Email address of the candidate"},
                    "phone": {"type": "string", "description": "Phone number of the candidate"},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "List of candidate skills"},
                    "education": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "degree": {"type": "string"},
                                "institution": {"type": "string"},
                                "year": {"type": "string"}
                            }
                        },
                        "description": "Educational background"
                    },
                    "work_experience": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "company": {"type": "string"},
                                "duration": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        },
                        "description": "Work experience history"
                    }
                },
                "required": ["name", "email", "skills", "education", "work_experience"]
            }
        },
        "parse_job_posting": {
            "name": "parse_job_posting",
            "description": "Extract structured information from job posting text",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "company": {"type": "string"},
                    "location": {"type": "string"},
                    "required_skills": {"type": "array", "items": {"type": "string"}},
                    "preferred_skills": {"type": "array", "items": {"type": "string"}},
                    "description": {"type": "string"},
                    "responsibilities": {"type": "array", "items": {"type": "string"}},
                    "qualifications": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["title", "required_skills", "description"]
            }
        },
        "match_candidate_to_job": {
            "name": "match_candidate_to_job",
            "description": "Evaluate how well a candidate matches a job posting",
            "parameters": {
                "type": "object",
                "properties": {
                    "match_score": {"type": "number", "description": "Score from 0-100 indicating match quality"},
                    "missing_skills": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of skills the candidate is missing for this job"
                    },
                    "summary": {
                        "type": "string",
                        "description": "A detailed summary of how well the candidate matches the job"
                    }
                },
                "required": ["match_score", "missing_skills", "summary"]
            }
        },

        "generate_cover_letter": {
            "name": "generate_cover_letter",
            "description": "Generate a tailored cover letter based on candidate profile and job posting",
            "parameters": {
                "type": "object",
                "properties": {
                    "cover_letter": {"type": "string", "description": "Complete cover letter text"}
                },
                "required": ["cover_letter"]
            }
        }
    }
    
    # Ensure the function exists in our schema
    if function_name not in function_schemas:
        raise ValueError(f"Unknown function: {function_name}")
    
    try:
        # Call the OpenAI API with function calling - NEW API FORMAT
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or your preferred model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(arguments)}
            ],
            tools=[{
                "type": "function",
                "function": function_schemas[function_name]
            }],
            tool_choice={"type": "function", "function": {"name": function_name}}
        )
        
        # Extract the function call result - NEW API FORMAT
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == function_name:
            return tool_call.function.arguments
        else:
            raise ValueError(f"Unexpected function call: {tool_call.function.name}")
            
    except Exception as e:
        raise Exception(f"Error calling LLM API: {str(e)}")