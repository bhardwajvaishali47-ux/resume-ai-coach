import os
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser , StrOutputParser
from langchain_anthropic import ChatAnthropic

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# create prompt system message and human message 

system_message = """You are an expert recruitment consultant and career coach with 15 years of experience. Your job is to compare a candidate's resume against a job description and provide an honest , detailed assessment . You must return a valid JSON object only. No extra text. No explantion. No markdown. Just the raw JSON object.
"""

human_message = """Compare this resume against the job description  below.
Analyse carefully:
1. Which skills from the JD does the candidate have?
2. Which required skills are missing?
3. What are the candidate's strongest points for this role?
4. What are the gaps that would concern a recruiter?
5. Overall how strong is this application?

IMPORTANT RULES:
- strengths must ALWAYS contain exactly 3 items — never empty
- gaps must ALWAYS contain exactly 3 items — never empty
- Every candidate has genuine strengths — find them even if match is low
- match_score must be an integer between 0 and 100

Return a JSON object with exactly these keys:
- match_score: a number from 0 to 100 (integer only)
- matched_skills: list of skills candidate has that JD requires
- missing_skills: list of required skills candidate is missing
- strengths: list of 3 specific strengths for this exact role
- gaps: list of 3 specific gaps or concerns for this role
- recommendation: one sentence honest advice for the candidate

RESUME: {resume_text}

JOB DESCRIPTION : {job_description}


"""
# these prompts will be sent 
prompt = ChatPromptTemplate.from_messages([
    ("system" , system_message),
    ("human" , human_message)
])

parser = JsonOutputParser() # to get the output in json format 

jd_matcher_chain = prompt | llm | parser 

def match_resume_to_job(resume_text : str, job_description: str)-> dict:
    """ Takes resume text and job description as input.
    Returns match analysis with score , gaps , strengths, and recommendation"""
    
    result = jd_matcher_chain.invoke({
        "resume_text" : resume_text,
        "job_description" : job_description
    })
    
    return result

if __name__ == "__main__":
    with open("test_resume.txt", "r") as f:
        test_resume = f.read()

    with open("test_job_description.txt", "r") as f:
        test_jd = f.read()

    print("Matching resume to job description...")
    print("---")
    result = match_resume_to_job(test_resume, test_jd)
    print(json.dumps(result, indent=2))