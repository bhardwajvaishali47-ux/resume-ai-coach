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