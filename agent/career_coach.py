import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage , AIMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv() # invoke API url 

llm = ChatAnthropic(
    model ="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Why use build function here :- Because the system prompt needs to be different for every user. It contains their specific name, their specific skills, their specific match score. You cannot hardcode it. The function takes the analysis results and builds a personalised prompt for that specific user.

def build_system_prompt(
    parsed_resume : dict, job_description : str, match_result : dict) -> str:
    """Builds a detailed system prompt that injects the full resume analysis context into the agent before conversation starts. The agent knowds everything about the user before they ask theri first question. """
    
    # extracting data from dictionaries using .get()
    name = parsed_resume.get("name" , "the candidate")
    skills = parsed_resume.get("skills",[])
    experience= parsed_resume.get("experience",[])
    certifications = parsed_resume("certifications",[])
    match_score = match_result.get("match_score",0)
    matched_skills = match_result.get("matched_skills",[])
    missing_skills= match_result.get("missing_skills",[])
    strengths = match_result.get("strengths",[])
    gaps = match_result.get("gaps",[])
    recommendation = match_result.get("recommendation","")
    
    
    #This is a multi-line f-string. Everything between the triple quotes """ is one long string. The f prefix means all {variable} placeholders get filled with real values.
    # join() converts a Python list into a string. ', '.join(["Python", "SQL", "AWS"]) produces "Python, SQL, AWS". Without join, the list would appear as ['Python', 'SQL', 'AWS'] with brackets and quotes — ugly in a prompt.
    
    #experience[0]['role'] if experience else 'Not found'.This is a one-line conditional — called a ternary expression. It means:If experience list is not empty → get the first job's role,If experience list is empty → use "Not found"
    system_prompt = f"""You are an expert AI career coach with 15 years of experience 
helping professionals land their dream jobs.

You are currently helping {name} with their job application.
You have already analysed their resume and the job description.
You know everything about their profile. Be specific, personal, and actionable in every response.

===CANDIDATE RESUME SUMMARY===
Name : {name}
Skills :{', '.join(skills)} 
Experience : {len(experience)} roles
Most recent role : {experience[0]['role'] if experience else 'Not Found'} at {experience[0]['company'] if experience else 'Not Found'}
Certifications : {', '.join(certifications)}


==JOB DECRIPTION==
{job_description}

== MATCH ANALYSIS RESULTS==
Match Score: {match_score}%
Matched Skills : {', '.join(matched_skills)}
Missing Skills : {', '.join(missing_skills)}
Key Strengths : {chr(10).join(strengths)}
Key Gaps : {chr(10). join(gaps)}
Overall Recommendation : {recommendation}

=== YOUR BEHAVIOUR AS CAREER COACH ===
1. Always refer to the candidate by name
2. Give specific advice based on THEIR resume — not generic tips
3. When rewriting resume sections, tailor them to the job description above
4. Remember everything said in this conversation
5. If asked to improve something you already wrote, do it — you remember
6. Be honest about gaps but constructive and encouraging
7. Always end advice with one concrete next action the candidate can take"""

    return system_prompt
    
    