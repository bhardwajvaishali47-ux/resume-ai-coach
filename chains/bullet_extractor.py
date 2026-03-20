import os 
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

llm = ChatAnthropic(
     model="claude-sonnet-4-6",
    max_tokens=2048,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

system_message = """ 
You are a precise text extractor. Your only job is to extract bullet points from text.Return valid JSON only . No extra text.

"""

human_messsage = """  
Extract all bullet points from this text. Return them as a JSON object with this exact structure:
{{
    "bullets" : [
        "first bullet point text here",
        "second bullet point text here"

    ]
}}

If no bullet points are found return :
{{
    "bullets" : []
 }}
 
 Text to extract from :
 {text}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human" , human_messsage)
])

parser = JsonOutputParser()

bullet_extractor_chain = prompt | llm | parser

def extract_bullets_from_text(text: str) -> list:
    """
    Extracts bullet points from any text.
    Used to pull improved bullets from agent chat responses.

    Input:  text containing bullet points
    Output: list of bullet point strings
    """
    result = bullet_extractor_chain.invoke({"text": text})
    return result.get("bullets", [])



if __name__ == "__main__":
    test_text = """
    Here are your improved BT Group bullets for Flipkart:

    • Defined product vision and owned AI platform roadmap
      serving 10M+ broadband customers, delivering 30%
      reduction in reporting latency
    • Integrated Vertex AI to automate KPI insights,
      reducing manual analysis effort by 25%
    • Led cross-functional team of 8 engineers across
      6 agile sprints with 100% sprint commitment rate
    """

    bullets = extract_bullets_from_text(test_text)
    print("Extracted bullets:")
    for bullet in bullets:
        print(f"  • {bullet}")