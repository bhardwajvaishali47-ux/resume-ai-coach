import os
import json
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

system_message = """You are an expert resume parser.
Your only job is to extract information from resumes.
You must return a valid JSON object only.
No extra text. No explanation. No markdown code blocks.
Just the raw JSON object starting with {{ and ending with }}."""

human_message = """Extract all information from the resume below.

Return a JSON object with these exact keys:
- name: full name as string
- email: email address as string  
- phone: phone number as string
- summary: professional summary as string
- skills: list of skills as array of strings
- experience: list of jobs, each with company, role, duration, bullets
- education: list of degrees, each with degree, institution, year
- certifications: list of certifications as array of strings

If any field is not found in the resume, use empty string or empty list.

RESUME:
{resume_text}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", human_message)
])

parser = JsonOutputParser()

resume_parser_chain = prompt | llm | parser


def parse_resume(resume_text: str) -> dict:
    """
    Takes raw resume text as input.
    Returns structured dictionary with all resume information.
    """
    result = resume_parser_chain.invoke({
        "resume_text": resume_text
    })
    return result


if __name__ == "__main__":
    with open("test_resume.txt", "r") as f:
        test_resume = f.read()

    print("Parsing resume...")
    print("---")
    result = parse_resume(test_resume)
    print(json.dumps(result, indent=2))