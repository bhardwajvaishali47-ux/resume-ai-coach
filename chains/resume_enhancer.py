import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from chains.bullet_extractor import extract_bullets_from_text

load_dotenv()

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

system_message = """You are a precise resume data extractor.
Your only job is to identify which company's bullets
were rewritten in a career coach conversation.
Return valid JSON only. No extra text."""

human_message = """Look at this career coach conversation message.
Identify if it contains rewritten resume bullet points
for a specific company or role.

Return JSON with this exact structure:
{{
    "contains_rewrites": true or false,
    "company_name": "company name if found, empty string if not",
    "has_bullets": true or false
}}

Message to analyse:
{message}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", human_message)
])

parser = JsonOutputParser()
identifier_chain = prompt | llm | parser

# Uses Claude to check if a chat message contains rewritten bullets. Returns a dictionary telling us whether the message has rewrites and for which company.
def identify_rewrite_message(message: str) -> dict:
    """
    Checks if a chat message contains rewritten bullets.
    Returns info about which company was rewritten.
    """
    result = identifier_chain.invoke({"message": message})
    return result


def enhance_resume_with_chat(
    parsed_resume: dict,
    chat_messages: list
) -> dict:
    """
    Scans chat history for rewritten bullet points.
    Merges improvements into the parsed resume dictionary.

    Input:
        parsed_resume: original parsed resume dictionary
        chat_messages: list of {role, content} from session_state

    Output:
        enhanced resume dictionary with improved bullets
    """
    import copy
    enhanced_resume = copy.deepcopy(parsed_resume)  #Makes a complete deep copy of the original resume dictionary. Deep copy means it creates entirely new nested objects — not just a reference to the same data. This is critical because we do not want to modify the original resume — only the copy.

    # Filtering assistant messages
    assistant_messages = [
        msg["content"]
        for msg in chat_messages
        if msg["role"] == "assistant" #Your chat history in session_state is a list of dictionaries like {"role": "user", "content": "..."} and {"role": "assistant", "content": "..."}. We only want the assistant's messages — Claude's responses — because that is where the rewrites are.
    ]

    if not assistant_messages:
        return enhanced_resume

    for message in assistant_messages:
        message_lower = message.lower()
        
        #Detecting bullet content
        has_bullets = (
            "•" in message or
            "- " in message or
            "rewritten" in message_lower or
            "improved" in message_lower or
            "stronger" in message_lower or
            "bullet" in message_lower
        )

        if not has_bullets:
            continue

        extracted_bullets = extract_bullets_from_text(message)

        if not extracted_bullets:
            continue

        experience = enhanced_resume.get("experience", [])
        if not experience:
            continue

        best_match_index = 0
        best_match_score = 0
        
        # Finding the best matching job
        # This is a simple word-matching algorithm. It checks how many words from the job's company and role appear in the chat message. The job with the highest score is assumed to be the one being rewritten.
        for i, job in enumerate(experience):
            company = job.get("company", "").lower()
            role = job.get("role", "").lower()

            combined = company + " " + role
            message_lower_check = message.lower()

            score = 0
            for word in combined.split():
                if len(word) > 3 and word in message_lower_check:
                    score += 1

            if score > best_match_score:
                best_match_score = score
                best_match_index = i

        if best_match_score > 0:
            enhanced_resume["experience"][best_match_index]["bullets"] = extracted_bullets
            enhanced_resume["experience"][best_match_index]["enhanced"] = True #flag to any job that was improved

    return enhanced_resume

# Below Function uses this flag to tell the user what was improved.
# Compares original and enhanced resume to produce a human-readable summary of improvements. Shows the user exactly what changed before they download.
def get_enhancement_summary(
    original_resume: dict,
    enhanced_resume: dict
) -> str:
    """
    Compares original and enhanced resume.
    Returns a summary of what was improved.
    """
    improvements = []

    original_exp = original_resume.get("experience", [])
    enhanced_exp = enhanced_resume.get("experience", [])

    for i, job in enumerate(enhanced_exp):
        if job.get("enhanced"):
            company = job.get("company", "Unknown")
            original_count = len(original_exp[i].get("bullets", []))
            new_count = len(job.get("bullets", []))
            improvements.append(
                f"{company}: {original_count} bullets → {new_count} improved bullets"
            )

    if improvements:
        return "Improvements applied:\n" + "\n".join(improvements)
    else:
        return "No improvements found in chat history."