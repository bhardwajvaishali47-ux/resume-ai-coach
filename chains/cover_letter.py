import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


system_message = """  
You are an expert cover letter writer with 15 years of experience helping professionals land senior roles at top tech companies.

You write cover letters that :
- Sound genuinely human -not templated or robotic
- open with the specific achievement that directly matches the role
- Show real understanding of the company and role
- Address gaps honestly and reframe them as strengths
- Are concise - maximum 4 paragraphs, under 400 words
- End with a confident , specifc call to action

You never use clichés like:
- "I am writing to apply for..."
- "I am a passionate and driven professional..."
- "I would be a great fit because..."
- "Please find my resume attached..."

Every letter must feel like it was written specifically
for this person and this company. No generic statements."""

human_message = """ Write a cover letter for this candidate.

==CANDIDATE PROFILE==
Name : {name}
Most Recent Role : {recent_role} at {recent_company}
Key Skills : {skills}
Certifications : {certifications}
Years of Experience : {years_experience}


==TARGET JOB==
{job_description}


===MATCH ANALYSIS===
Match Score : {match_score}%
Key Strengths for this role: {strengths}
Gaps to address : {gaps}
Overall recommendation : {recommendation}


====INSTRUCTIONS===
1. Open with the candidate's single strongest achievement that directly maps to this specific role
2. Paragraph 2 : connect their AI/data experience specifically to what this company is building
3. Paragraph 3: address the main gap honestly but reframe it as a perspective advantage, not a weakness
4. Closing: specific ask with confident tone

Write the complete cover letter now.
Address it to "Hiring Manager" since we do not know the same.
Start with the candidate's name and contact would be at the top.

"""
    
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", human_message)
])

parser = StrOutputParser()

cover_letter_chain = prompt | llm | parser

def generate_cover_letter(
    parsed_resume : dict,
    job_description : str,
    match_result : dict
) -> str:
    """ 
    Generates a personalised cover letter.
    
    Takes the complete analysis results and generates a tailored cover letter specific to this candidate and this job description.
    Returns the cover letter as a plain string.
    """
    
    name = parsed_resume.get("name", "Candidate")
    skills = parsed_resume.get("skills",[])
    experience = parsed_resume.get("experience",[])
    certifications = parsed_resume.get("certifications", [])
    
    
    
    recent_role = experience[0]["role"] if experience else "Not Specified"
    recent_company = experience[0]["company"] if experience else "Not Specified"
    
    
    years_experience = len(experience) * 2 #A rough estimate — assuming each job lasted about 2 years on average. Not perfect but reasonable for a cover letter.
    
    
    strengths = match_result.get("strengths", [])
    gaps = match_result.get("gaps" ,[])
    recommendation = match_result.get("recommendation" , "")
    match_score = match_result.get("match_score" ,0)
    
    result = cover_letter_chain.invoke({
        "name": name,
        "recent_role": recent_role,
        "recent_company": recent_company,
        "skills": ", ".join(skills[:10]), # takes only the first 10 skills. You have 28 skills — listing all of them in a cover letter would be overwhelming. The first 10 are most important.
        "certifications": ", ".join(certifications),
        "years_experience": years_experience,
        "job_description": job_description,
        "match_score": match_score,
        "strengths": "\n".join(strengths),
        "gaps": "\n".join(gaps),
        "recommendation": recommendation
        
        
    })
    return result


if __name__ == "__main__":
    import json

    test_resume = {
        "name": "Vaishali Bhardwaj",
        "skills": ["Product Management", "LLMs", "GCP", "Agile", "PRD Writing"],
        "experience": [
            {
                "role": "Product Owner / Product Manager",
                "company": "BT Group (Openreach)",
                "duration": "Dec 2021 - Jan 2026"
            }
        ],
        "certifications": ["Google Cloud Certified Generative AI Leader"]
    }

    test_jd = """Senior AI Product Manager at Flipkart.
    Looking for 7+ years PM experience with AI/ML products.
    Must have strong PRD writing and stakeholder management."""
    
    test_match = {
        "match_score": 72,
        "strengths": [
            "Strong AI/ML product background with Vertex AI",
            "Google Cloud certification directly relevant"
        ],
        "gaps": [
            "No ecommerce experience",
            "Limited consumer product background"
        ],
        "recommendation": "Strong candidate but must address ecommerce gap"
    }

    print("Generating cover letter...")
    print("---")
    letter = generate_cover_letter(test_resume, test_jd, test_match)
    print(letter)


