# Architecture decision record 
# Project : Resume AI Coach 
# Author : Vaishali Bhardwaj
# Started: March 2026

## Decision 1 - Project Folder Structure 

### What we created 
- chains/ - Langchain files (parser, matcher, rewriter)
- toos/ - Langchain agent tools (PDF reader , jobs API , cover letter)
- docs/ - Documentation (descision/ architecture)
- .env - API keys (never goes to Github)
- .gitignore - Tells Git which files to ignore 

### Why this strucutre 
Seperations of concerns - each folder has one responsibiity 
Clean architecture makes the project readable , maintainable and impressive to technical reviewers

### Gen AI Concepts it maps to 
- chains/ -> Langchain chain concepts
- tools/ -> Langchian Agent and Tools concepts
- .env -> API security and key management

## Descision 2 - Model Choice : Claude Sonnet (claude -sonnet -4-6)
### Why claude sonnet over GPT-4o
1. 200,000 token context windo vs GTP-4o's 128,000
-> Entire resume + JD + Full chat hisotry fits in one call 
-> No complex memory management needed for most sessions 

2. Superior Strucutre JSON extraction 
-> Resume parsing requires requires reliable JSON output
-> Claude Sonnet produces cleaner structured  data 

3. Deliberate differentiation 
-> Every tutorial uses openAI
-> Using claude shows reasoned descision making (PM thinking)

### Cost per session 
- Average session ~ 5000 tokens
- Cost at sonnet pricing ~ 0.02 per session 
- $5 credit ~~ 250 full test sessions 

## Decision 3 - Framwork : Langchain 
### Why Langchain over raw Anthropic  SDK 
Raw SDK = send text , get text back .That is all .
Langchain adds :-
- Chains : sequence multiple steps cleanly 
- Agents : model decides what tool to call 
- Memory : conversation hisotry managed automatically 
- Tools : give model access to real functions 
- Langsmith : observer every reasoning step (chain of thought)

Building all of this from sratch = week of work 
Langchain is industry standard for production LLM apps 

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept clarification — SDK vs LangChain vs Claude

ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically

## Concept Clarification  - SDK vs Langchain vs Claude 
ANTHROPIC SDK (library name: anthropic)
- Direct communication layer to Claude's API
- Handles HTTP requests, authentication, response parsing
- One job: send message to Claude, get message back

LANGCHAIN (library name: langchain)
- Orchestration layer built on top of the SDK
- Adds chains, memory, agents, tools
- Uses the SDK internally to talk to Claude

CLAUDE (the actual AI model)
- Runs on Anthropic's servers, never locally
- Our app sends text, Claude thinks, response comes back
- We use claude-sonnet-4-6 specifically
Stack order:
Our Python code → LangChain → Anthropic SDK → Claude API

# Day 1 Learning - First API call 
### What I built 
day1_raw_api.py - a pythin file that calls Claude directly using Anthropic SDK and prints the response in terminal 

### What I learned 
- import os - reads environmental variables from Mac's memory 
- load_dotenv() - load .env file into memory at runtime 
- os.getenv() - retireves the API key safely 
- anthropic.Anthropic(api_key=) - creates the client connection 
- client.messages.create() - sends the actual request to claude 
- message.content[0].text - extract Claude's text response 

### Debugging I did 
- Fixed space after = sign in .env file (API key )
- Created fresh API key when old one was not working 
- used cat.env command to verify file contents 

### Key Insight
The code never runs claude locally . My mac sends text to Anthropic's servers , Claude thinks there, response come back. My Mac is just a messenger 


## Day 2 - Resume Parser Chain
### File : chains/ resume_parser.py


### WHY THIS FILE EXISTS 
When a user uploads their resume, the app needs to convert unstructured PDF text into strucutred data(JSON) that every other part of the app can work with .

The matcher chain needs it .
The rewriter chain needs it .
The chat agent needs it.
Everything depedends on this file working well correctly.

### THREE STEP FLOW
STEP 1: ChatPromptTemplate 
File Location : defined in resume_parser.py as variable "prompt"
What it does :
- Takes raw resume text as input via {resume_txt} placeholder
- Combines a system message (role instructions) with a human message (the actual task + resume data)
- Outputs a fully formatted prompt ready to send to Claude 

Why we need it :
- Every resume is different, we cannot hardcode text
- the {resume_text} placeholder gets replaced with actual resume content each time the chain runs
- without template , we would rewrite the prompt, every single time . Template = write once, use forever

If something breaks here :
- check that {resume_text} placeholder exist in human message
- check that the variable name passed to .invoke() matches exaclty : resume_parser_chain.invoke ({"resume_text" : text})
- If names do not match , Langchain throws a KeyError

STEP 2 : ChatAnthropic (Claude Sonnet)
File location : defined in resume_parser.py as variablen"llm"
What it does :-
- Receives the formatted prompt from Step 1
- Sends it to Anthropic's servers via API
- Claude reads the resume and extracts all the information 
- Returns a response  containing JSON  as text 

Why Claude Sonnet specifically :
- 200,000 token context window (fits any resume easily)
- Best at structured data extraction among available models
- More cost effective than Opus for this task 
- max_tokens = 2048 becuase the JSON output can be 500-800 tokens 

STEP 3 : JsonOutputParser
File Location : defined in resume_parser.py as variable "parser"
What it does :
- Receives Claude's text response from Step 2
- Strips any extra conversational text Claude may have added
- Extracts the JSON object from the response
- Converts the JSON string into a Python dictionary

Why we need it:
- Claude is a language model, it naturally adds text
- Without parser, we get: "Here is the JSON: {...} Hope this helps!"
- With parser, we get only: {"name": "John", "skills": [...]}
- Python cannot use a string as data, needs a dictionary

If something breaks here:
- If you get JSONDecodeError, Claude returned invalid JSON
- Fix: make prompt stricter - "return JSON only, no extra text"
- If fields are empty, the resume text did not reach Claude
- Fix: check {resume_text} placeholder and invoke() call

### HOW THE THREE STEPS CONNECT 
resume_parser_chain = prompt | llm | parser

The | symbol is the LCEL pipe operator.
LCEL = LangChain Expression Language.
It means: output of left flows as input to right.

Reading left to right:
prompt takes {resume_text} → fills template → passes to llm
llm receives prompt → calls Claude API → passes response to parser
parser receives response → extracts JSON → returns dictionary

This entire chain runs with one line:
result = resume_parser_chain.invoke({"resume_text": resume_text})

### THE FUNCTION WRAPPER

def parse_resume(resume_text: str) -> dict:

Why wrap the chain in a function?
- Other files call parse_resume(text) — simple and clean
- They do not need to know about chains, templates, parsers
- If we change the chain internals later, other files
  are not affected. They still just call parse_resume().
- This is called ABSTRACTION in software engineering.

resume_text: str means the input must be a string
-> dict means the function returns a dictionary
These are called TYPE HINTS — documentation for humans,
Python does not enforce them but they make code readable.

### THE TEST BLOCK

if __name__ == "__main__":

This block only runs when you execute this file directly:
python chains/resume_parser.py

It does NOT run when another file imports this file:
from chains.resume_parser import parse_resume

Why this matters:
- You can test resume_parser.py directly without
  running the whole app
- When app.py imports parse_resume, the test code
  does not execute and waste API credits

### THE SYSTEM MESSAGE — PROMPT ENGINEERING TECHNIQUES USED

system_message = "You are an expert resume parser..."

Technique 1 — Role Prompting
"You are an expert resume parser"
Giving Claude a specific expert role improves output quality.
Claude responds differently as a "resume parser" vs
as a "general assistant."

Technique 2 — Constraint Setting
"Return valid JSON only. No extra text."
Explicitly forbidding unwanted output.
Without this, Claude adds conversational text that
breaks the JsonOutputParser.

Technique 3 — Structured Output Instructions
Describing each field clearly:
"skills: list of skills as array of strings"
Removes ambiguity. Claude knows exactly what format
each field should be in.


### GENAI CONCEPTS IN THIS FILE

Prompt Engineering → system_message and human_message design
Role Prompting → "You are an expert resume parser"
Structured Output → describing exact JSON fields expected
LangChain Chains → prompt | llm | parser (LCEL)
Output Parsing → JsonOutputParser cleans Claude's response
Abstraction → parse_resume() hides chain complexity
Context Window → why we chose Claude Sonnet (200k tokens)


### DEBUGGING CHECKLIST FOR THIS FILE
If the chain returns empty fields:
□ Run: cat test_resume.txt (verify file has content)
□ Check {resume_text} placeholder in human_message
□ Check invoke() call passes "resume_text" key exactly
□ Add print(resume_text) before invoke() to verify text

If the chain throws an API error:
□ Check .env file: ANTHROPIC_API_KEY=sk-ant-... (no spaces)
□ Check credits at console.anthropic.com
□ Run: cat .env to verify key is complete

If the chain throws JSONDecodeError:
□ Claude returned text instead of JSON
□ Make system_message stricter about JSON only output
□ Check model name is exactly "claude-sonnet-4-6"

If imports fail:
□ Check (venv_ai) is showing in terminal
□ Run: source venv_ai/bin/activate
□ Run: pip install -r requirements.txt

## Day 3 - JD Matcher Chain
### File : chains/jd_matcher.py

### Why this file exist 
After parsing the resume into structured JSON, the app needs to compare that resume against a job description and answer:
- How well this person match this job ?
- What skills are they missing ?
- What are their strenghts for this specific role ?
- What should they do before applying ?

This the core feature of the product . Every competitor charges money for this . We built it from scratch using Claude's semantic understanding .

### WHAT IS NEW COMPARED TO DAY 2 ?
Day 2 Parser  had one input variable : {resume_text}
Day 3 matcher has two input variables : {resume_text} AND {job_description}

Both placeholders sits in the same human message. Both get filled when invoke() is called. Claude sees both in the same prompt and compares them.

invoke() call passes both values by mean : jd_matcher_chain.invoke({"resume_text" : resume_text, "job_descriptio" : job_description})

Critical rule : placeholder name in prompt must exactly match the key  name passed to invoke(). One letter difference causes a Key Error .

### THE THREE STEP FLOW 
STEP 1: ChatPromptTemplate
- Takes TWO variables: {resume_text} and {job_description}
- System message uses persona prompting:
  "expert recruitment consultant with 15 years experience"
- Human message uses chain of thought prompting:
  numbered questions guide Claude to reason step by step
  before producing the output
- Output: formatted prompt with both inputs ready for Claude

If something breaks here:
- Check both placeholders exist in human_message
- Check invoke() passes both keys with exact same names
- KeyError means placeholder name and key name do not match

STEP 2: ChatAnthropic (Claude Sonnet)
- Receives prompt containing both resume and JD
- Compares them using genuine semantic understanding
  NOT keyword matching
- Returns JSON analysis as text
- Output: AIMessage containing JSON string

If something breaks here:
- Check API key and credits as always
- If score seems wrong, improve system message
- Add "be strict and honest" to get more accurate scores

STEP 3: JsonOutputParser
- Strips any extra text from Claude's response
- Converts JSON string to Python dictionary
- Output: usable structured data your app can work with

If something breaks here:
- JSONDecodeError means Claude added text around the JSON
- Fix: make system message stricter about JSON only output

### THE FUNCTION

def match_resume_to_job(resume_text: str, job_description: str) -> dict:

Two parameters this time — both required.
Same abstraction pattern as Day 2.
Other files call this without knowing about the chain.

Future usage in app.py:
result = match_resume_to_job(parsed_resume, user_pasted_jd)
result["match_score"]     → 82
result["missing_skills"]  → ["Kubernetes", "CI/CD"]
result["recommendation"]  → "Strong candidate..."

### PROMPT ENGINEERING TECHNIQUES USED IN THIS FILE

Technique 1 — Persona Prompting
"expert recruitment consultant with 15 years of experience"

Why it works:
Claude was trained on billions of documents including
text written by recruitment consultants and HR professionals.
Giving it this specific expert identity makes it draw on
that specific knowledge pool.
"General assistant" gives generic answers.
"Expert recruiter with 15 years experience" gives answers
that sound like a real recruiter wrote them.

Technique 2 — Chain of Thought Prompting
Numbered questions force step by step reasoning:
1. Which skills from the JD does the candidate have?
2. Which required skills are missing?
3. What are the candidate's strongest points?
4. What are the gaps that would concern a recruiter?
5. Overall how strong is this application?

Why it works:
Research on LLMs shows that models give significantly
better answers when guided to reason step by step.
Without this, Claude jumps to a conclusion.
With this, Claude thinks through each dimension first
then produces a more accurate and detailed output.
This is called chain of thought prompting — one of the
most important techniques in prompt engineering.

Technique 3 — Output Constraints
"match_score: a number from 0 to 100 (integer only)"

Why it works:
Without "integer only" Claude might return "78%" or 78.5
Both would break downstream code expecting a clean number.
Explicit format constraints in prompts prevent
output format issues before they happen.

### THE MOST IMPORTANT CONCEPT — SEMANTIC UNDERSTANDING

This is what makes our app better than every
keyword matching tool on the market.

KEYWORD MATCHING — how Jobscan and basic ATS work:

They look for exact words only.

Example:
JD says:     "payments infrastructure"
Resume says: "payment integration project"

Keyword tool asks: does "payments infrastructure"
appear word for word in the resume?
Answer: NO
Result: marked as missing — WRONG ANSWER

These tools can be gamed by stuffing exact keywords
from the JD into your resume.
They have no understanding of meaning or context.
They are essentially Ctrl+F on a document.

SEMANTIC UNDERSTANDING — how Claude works:

Claude understands meaning and context, not just words.

Example:
JD says:     "payments infrastructure"
Resume says: "payment integration project"

Claude asks: do these mean the same thing in context?
- payment integration = building payment systems
- payments infrastructure = building payment systems
Answer: YES — same domain, same type of work
Result: correctly identified as a match 

Claude also connected:
"led team of 4 engineers" → "mentor junior engineers"
"40% API performance improvement" → "APIs serving millions"
These connections require understanding, not word matching.

WHY SEMANTIC UNDERSTANDING WORKS — THE TECHNICAL REASON

When Claude was trained, every word and concept was
converted into a vector — a list of numbers representing
its meaning. Think of it as coordinates on a map.

"payments"       → coordinates on meaning map: area X
"payment"        → very close to "payments" on the map
"infrastructure" → coordinates on meaning map: area Y
"integration"    → very close to "infrastructure" on map

Words with similar meanings have similar coordinates.
They cluster together on the meaning map.
Words with completely different meanings are far apart.

"payments" and "financial transactions" → close together
"payments" and "cooking techniques"     → far apart

When Claude compares resume to JD, it compares locations
on this meaning map — not the words themselves.
This is why it catches matches that keyword tools miss.

This same concept — converting text to vectors —
is what powers our RAG system in Week 3.
Embeddings, vector stores, semantic search —
all built on this same foundation.

WHAT THIS MEANS FOR YOUR PRODUCT

Keyword matching tools:
- Miss matches where same concept uses different words
- Can be gamed by keyword stuffing
- Give false negatives — good candidates marked as poor fit
- No reasoning, just a percentage

Our app with Claude:
- Catches matches based on meaning not just words
- Cannot be gamed by keyword stuffing
- Gives accurate match scores with specific reasoning
- Explains WHY each skill matches or is missing
- Sounds like a human recruiter, not a word counter

THE ONE SENTENCE FOR INTERVIEWS

"Unlike keyword matching tools that check for exact word
presence, our app uses Claude's semantic understanding
to compare meaning and context — the same way a human
recruiter reads a resume. This gives significantly more
accurate match scores and actionable gap analysis."

### GENAI CONCEPTS IN THIS FILE

Prompt Engineering      → system and human message design
Persona Prompting       → expert recruitment consultant role
Chain of Thought        → numbered reasoning steps
Multi-variable Input    → two placeholders in one template
LCEL Chains            → prompt | llm | parser
Output Parsing          → JsonOutputParser
Semantic Understanding  → meaning comparison not word matching
Vectors and Embeddings  → foundation of semantic understanding
                          (used fully in Week 3 RAG system)
Abstraction             → match_resume_to_job() hides chain

### DEBUGGING CHECKLIST FOR THIS FILE

If you get KeyError:
□ Check placeholder names in human_message
  {resume_text} and {job_description} must exist
□ Check invoke() keys match exactly:
  {"resume_text": ..., "job_description": ...}

If match_score seems inaccurate:
□ Add to system_message: "Be strict and honest.
  Score above 80 only for genuinely strong candidates."
□ Check job description has clear requirements listed

If missing_skills is empty when it should not be:
□ Run: cat test_job_description.txt to verify content
□ Check job description has explicit requirements section

If strengths or gaps are too generic:
□ Add to human_message: "Be specific. Reference actual
  companies, projects, and numbers from the resume."

If JSONDecodeError:
□ Strengthen system_message: "Return JSON only.
  No text before or after the JSON object."

If API error:
□ Check .env file: ANTHROPIC_API_KEY=sk-ant-... no spaces
□ Check credits at console.anthropic.com
□ Check model name: "claude-sonnet-4-6"