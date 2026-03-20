import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage , AIMessage, SystemMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from vectorstore.embedder import retrieve_relevant_knowledge

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
    certifications = parsed_resume.get("certifications",[])
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
    
#Building agent with memory 
def build_career_coach(parsed_resume : dict, job_description : str, match_result : dict):
    """ Builds a conversational career coach agent . Injects full resume analysis as context before conversations start.
    Returns an agent ready to chat with full memory."""
    
    system_prompt = build_system_prompt(parsed_resume , job_description, match_result)
    
    prompt = ChatPromptTemplate.from_messages([
        
        SystemMessage(content= system_prompt),#The complete briefing document you built in build_system_prompt(). Contains the user's full resume, job description, match analysis, and behaviour instructions. This is injected once and stays for the entire conversation.
        
        MessagesPlaceholder(variable_name= "history"), #This is the memory slot. Every time the chain runs, LangChain automatically fills this placeholder with the complete conversation history — every human message and every AI response from previous turns.Without this placeholder, Claude would forget every previous message. With it, Claude sees the entire conversation every time.
        
        ("human", "{input}") #The current message the user just typed. {input} is the variable that gets filled when you call agent_with_memory.invoke({"input": user_message}).
    ])
    
    chain = prompt | llm
    
    message_history = ChatMessageHistory()#This is the in-memory store that holds all conversation messages. It is a simple list of HumanMessage and AIMessage objects that grows with every exchange.Every time the user says something, it gets added here. Every time Claude responds, that gets added here too. This list is what gets inserted into the MessagesPlaceholder on every call.
    
    agent_with_memory = RunnableWithMessageHistory(
        chain,
        lambda session_id : message_history, #lambda session_id: message_history — a function that returns the message history for a given session. The lambda is a tiny anonymous function. When called with any session_id, it returns your message_history object. This design allows multiple users to have separate histories in a real app.
        
        input_messages_key="input", #tells the memory manager that the user's current message is stored under the key "input" in your invoke call.
        history_messages_key="history" #ells the memory manager to inject conversation history into the placeholder named "history" in your prompt.
    )
    #agent_with_memory — to call when user sends a message.
    #message_history — to read the conversation history for displaying the chat on screen. Streamlit needs to know what was said to render the chat bubbles correctly.
    return agent_with_memory, message_history 

#This is the function your UI calls every time the user sends a message.
def chat_with_coach(agent_with_memory, user_message : str) -> str:
    """" Sends a message to the career coach and gets a response.
    Now enhanced with RAG — retrieves relevant knowledge
    from knowledge base before answering. """
    
    relevant_knowledge = retrieve_relevant_knowledge(user_message)
    
    enhanced_message = f"""{user_message}
    [RELEVANT EXPERTISE FROM KNOWLEDGE BASE]
    {relevant_knowledge}
     [END OF KNOWLEDGE BASE CONTEXT]

    Please use the above knowledge base context to ground 
    your advice in proven best practices."""  
    
    
    
    
    response = agent_with_memory.invoke(
        {"input" : enhanced_message}, #Runs the full chain. Automatically reads history, builds complete prompt with system context + history + new message, sends to Claude, gets response, saves response to history.
        config = {"configurable" : {"session_id" : "career_session"}} #Tells the memory manager which session this message belongs to. We use a fixed string "career_session" because there is only one conversation per app session. In a multi-user production app, this would be a unique user ID.
    )
    
    return response.content #Extracts Claude's text from the response object. Returns it as a plain string to the UI.


    
