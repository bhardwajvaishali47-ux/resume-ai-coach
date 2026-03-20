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

## Day 4- PDF Reader Tool and Complete Pipeline
### Files : tools/pdf_reader.py and pipeline.py

### WHY THESE FILES EXIST
Until Day 3, all chains worked with plain text files.
Real users upload PDF files. Day 4 solves this.

pdf_reader.py — reads any PDF and returns clean text
pipeline.py — connects all three components into one flow


### FILE 1: tools/pdf_reader.py
URPOSE:
Takes a PDF file path as input.
Returns clean extracted text as output.
Every other part of the app depends on this working correctly.

THREE FUNCTIONS INSIDE:

1. clean_text(text: str) -> str
   Fixes two problems that appear in extracted PDF text:
   
   Problem 1: Font encoding artifacts
   Some PDFs use custom bullet symbols.
   pdfplumber cannot decode them and writes (cid:127) instead.
   clean_text replaces every (cid:xxx) with a proper bullet •
   
   Problem 2: Irregular spacing
   PDFs sometimes have multiple spaces or extra newlines.
   clean_text replaces any sequence of whitespace with one space.
   
   Library used: re (regular expressions)
   re is built into Python — no installation needed.
   re.sub(pattern, replacement, text) finds and replaces patterns.
   
   This is called defensive cleaning — fixing known problems
   before they cause issues downstream.

  2. extract_text_from_pdf(file_path: str) -> str
   The main working function.
   Opens PDF with pdfplumber.
   Loops through every page.
   Extracts text from each page.
   Calls clean_text() to fix encoding issues.
   Returns cleaned text string.
   
   Error handling:
   If extracted text is less than 100 characters,
   the PDF is likely image-based (scanned document).
   Returns an ERROR: string instead of crashing.
   This is called defensive programming.
   
   TWO TYPES OF PDFs EXIST IN THE REAL WORLD:
   Type 1 — Text-based: created from Word, Google Docs, Pages
            Text is stored as characters. pdfplumber reads it. 
   Type 2 — Image-based: scanned paper documents
            Text is a photo. pdfplumber sees nothing. 
            Our error handling catches this gracefully.

3. read_pdf(file_path: str) -> str  — decorated with @tool
   LangChain tool version of the same function.
   The @tool decorator registers it with LangChain.
   The AI agent will call this in Week 2 when it needs to read a PDF.
   Internally just calls extract_text_from_pdf().
   
   WHY TWO VERSIONS OF THE SAME FUNCTION:
   extract_text_from_pdf = direct Python call (used in pipeline.py)
   read_pdf with @tool = agent call (used by LangChain agent)
   Having both avoids issues with @tool decorator machinery
   when calling the function directly from Python code.


DEBUGGING CHECKLIST:
□ If output is empty: run cat yourfile.pdf won't work — use
  python tools/pdf_reader.py yourfile.pdf to test directly
□ If (cid:127) appears in output: clean_text() is not running
  check that clean_text() is called before returning
□ If ERROR appears: PDF is image-based or corrupted
  ask user to export from Word or Google Docs instead
□ If pdfplumber import fails: run pip install pdfplumber


### FILE 2: pipeline.py

PURPOSE:
Master orchestration file.
Connects pdf_reader, resume_parser, jd_matcher into one flow.
Single function call runs the entire analysis.

CONCEPT — WHAT IS AN ORCHESTRATION LAYER:
Individual components (pdf_reader, parser, matcher) each
do one job independently. They do not know about each other.
pipeline.py coordinates them — tells each one what to do
and passes results from one to the next.
This is called an orchestration layer.
Same concept used in production systems everywhere.

THE FLOW:
PDF file path
      ↓
extract_text_from_pdf() — tools/pdf_reader.py
      ↓
Plain text string
      ↓
      ├──→ parse_resume() — chains/resume_parser.py
      │         ↓
      │    Structured JSON dictionary
      │
      └──→ match_resume_to_job() — chains/jd_matcher.py
                ↓
           Match analysis dictionary

Both results returned together in one dictionary.

THE FUNCTION:
def analyze_resume(pdf_path: str, job_description: str) -> dict

Input 1: pdf_path — file path to the PDF on disk
Input 2: job_description — job description as plain text string
Output: dictionary with two keys:
        "parsed_resume" — structured resume data
        "match_result"  — score, gaps, strengths, recommendation

WHY ONE MASTER FUNCTION:
When Streamlit UI is built (Day 5), the entire UI calls
this one function when user clicks Analyse button.
The UI does not need to know about chains or tools.
It calls analyze_resume() and gets everything back.
This is abstraction — hiding complexity behind a simple interface.

ERROR HANDLING IN PIPELINE:
if resume_text.startswith("ERROR"):
    return {"error": resume_text}

If PDF reading fails, pipeline stops immediately.
Returns error dictionary instead of crashing.
Steps 2 and 3 never run if Step 1 fails.
This is called fail-fast — detect problems early and stop cleanly.

KEY LESSON — INDENTATION BUG:
if __name__ == "__main__": must be at ZERO indentation.
If it is indented inside the function, it never runs.
Python uses indentation to determine which block code belongs to.
The function ends at the return statement.
Everything after return at same indentation is unreachable.

VARIABLE NAMING LESSON:
Never name a variable the same as the function you imported.
Wrong: parse_resume = parse_resume(text)  ← overwrites function
Right: parsed_resume = parse_resume(text) ← different name
After the wrong version, calling parse_resume() again crashes
because Python finds the variable, not the function.

DICTIONARY KEY CONSISTENCY:
Return key names must match everywhere in your code.
Wrong: return {"matched_result": result}
Right: return {"match_result": result}
One letter difference causes KeyError when accessing result.

---

### NEW PYTHON CONCEPTS LEARNED TODAY

tempfile (used in Day 5 — documented now for reference):
Built-in Python library.
Creates temporary files on disk.
Needed because Streamlit holds uploaded files in memory
but pdfplumber needs a real file path to open.
tempfile bridges this gap.

regular expressions (re library):
Built-in Python library.
re.sub(pattern, replacement, text) finds and replaces patterns.
Used in clean_text() to fix PDF encoding artifacts.
Think of it as a powerful find-and-replace.

@tool decorator:
LangChain decorator that registers a function as an agent tool.
The agent reads the function's docstring to decide when to call it.
Clear, specific docstrings are critical for agent tool selection.

.get() dictionary method:
Safe way to access dictionary keys.
parsed_resume.get('skills', [])
Returns empty list [] if 'skills' key does not exist.
Prevents KeyError crashes when Claude misses a field.

f-strings:
f"Found {len(skills)} skills"
The f prefix makes {} into evaluated expressions.
Whatever is inside {} gets calculated and inserted as text.

---

### WHAT WAS TESTED TODAY

Tested pipeline.py with real resume:
File: Vaishali_Bhardwaj_ProductManager_AI.pdf
JD: Senior AI Product Manager at Razorpay

Results:
- 4083 characters extracted from PDF
- 21 skills identified
- 4 jobs found
- Match score: 82%
- 16 matched skills
- 3 gaps: fintech experience, vector databases, startup pace
- Recommendation: strong candidate, address fintech gap

This confirmed the entire backend pipeline works correctly
end to end with a real PDF and real job description.

---

### GENAI CONCEPTS IN THESE FILES

Orchestration layer  → pipeline.py coordinates components
Defensive programming → error handling at every step
Abstraction          → one function hides all complexity
Tool pattern         → @tool decorator for agent use
Semantic matching    → raw text passed to matcher not JSON
                       (preserves linguistic context for Claude)


## Day 5- Streamlit UI
### File : app.py

### WHY THIS FILE EXIST
The backend pipeline was complete aftewr day 4
But users cannot run python scripts. They need a web interface - a real app in a browser. app.py is that interface. it connects everything the user sees to everything the backedn does.

### WHAT IS STREAMLIT
Streamlit is a python library that turns python scripts  into web applications without writing HTML, CSS or javascript. You write python. Steamlit renders a real web page . One line of python = a file uploader, button, chart , etc

Why Streamlit for this project:
- Already know Python — no new language needed
- File upload built in — perfect for PDF resumes
- Runs locally during development
- Deploys to cloud in minutes (free)
- Industry standard for AI/ML demos and prototypes

### THE STREAMLIT EXECUTION MODEL — CRITICAL CONCEPT
Regular Python script:
Runs top to bottom → finishes → done

Streamlit app:
Runs → browser opens → waits
User interacts (clicks, uploads, types)
→ ENTIRE SCRIPT RERUNS from top to bottom
→ waits again
→ user interacts again
→ ENTIRE SCRIPT RERUNS again
→ repeats forever

Every single interaction triggers a full rerun.
This is called the Streamlit execution model.

Problem this creates:
If user clicks Analyse and results are calculated,
then user scrolls — script reruns — results disappear.

Solution: st.session_state


### ST.SESSION_STATE — HOW RESULTS SURVIVE RERUNS
st.session_state is a dictionary that persists across reruns.
Unlike regular variables which reset on every rerun,
session_state values stay until the browser tab is closed.

Store a result:
st.session_state["result"] = analysis_result
st.session_state["analysis_done"] = True

Read it back on next rerun:
if st.session_state.get("analysis_done"):
    result = st.session_state["result"]
    display(result)

Think of it as a sticky note on a whiteboard.
Even when the whiteboard gets wiped (script reruns),
the sticky note stays.

Used in our app to store:
- analysis_done: True/False flag
- result: the complete pipeline output dictionary

### TEMPFILE — BRIDGING MEMORY AND DISK
This is one of the trickiest concepts in the UI.

The problem:
When user uploads PDF, Streamlit holds it in memory.
There is no file path — just bytes in RAM.
But extract_text_from_pdf() needs a real file path.
pdfplumber cannot open a memory object.

The solution: tempfile library (built into Python)

How it works:
1. User uploads PDF → Streamlit holds bytes in memory
2. tempfile.NamedTemporaryFile() creates a real file on disk
3. tmp_file.write(uploaded_file.getvalue()) writes bytes to disk
4. tmp_path = tmp_file.name gives us the real file path
5. analyze_resume(tmp_path, ...) uses that path
6. os.unlink(tmp_path) deletes the temporary file


delete=False means the file stays on disk after the
with block closes — needed because analyze_resume()
reads it after the with block ends.

os.unlink(tmp_path) manually deletes it after use.
Always clean up temporary files.

### THE FIVE STREAMLIT COMPONENTS USED

st.set_page_config()
Must be the VERY FIRST Streamlit call in the file.
Sets browser tab title, icon, and layout.
layout="wide" uses full browser width.

st.columns(2)
Splits the page into side by side sections.
col1, col2 = st.columns(2)
with col1: — everything here goes in left column
with col2: — everything here goes in right column

st.file_uploader()
Creates drag and drop file upload area.
type=["pdf"] restricts to PDF files only.
Returns uploaded file object or None if empty.

st.text_area()
Multi-line text input box.
height=300 sets box height in pixels.
placeholder shows grey hint text when empty.

st.button()
Creates clickable button.
Returns True when clicked, False otherwise.
type="primary" makes it blue/prominent.
use_container_width=True stretches to full width.

st.spinner()
Shows animated loading indicator.
Used during the 20-30 second analysis wait.
Disappears automatically when code inside finishes.
Critical for user experience — without it app looks frozen.

st.progress()
Visual progress bar.
Takes value between 0 and 1.
score / 100 converts 0-100 score to 0-1 range.

st.success() / st.warning() / st.error()
Coloured message boxes — green, yellow, red.
Used for colour coded feedback based on match score.
Above 75% = green success
50-75% = yellow warning
Below 50% = red error

st.expander()
Collapsible section — collapsed by default.
User clicks to expand and see content inside.
Used for raw JSON data — available but not intrusive.

st.json()
Displays Python dictionary as formatted JSON.
Collapsible and searchable in the browser.

---

### INPUT VALIDATION — WHY IT MATTERS
Before running expensive API calls, always validate inputs.

if uploaded_file is None:
    st.warning("Please upload your resume PDF first.")
elif not job_description.strip():
    st.warning("Please paste a job description first.")

Why:
- Prevents API calls with empty data
- Saves API credits
- Gives user clear guidance
- Professional user experience
- Never trust user input — always validate

This is a fundamental product development principle.

---

### THE COMPLETE FLOW IN APP.PY

User opens browser at localhost:8501
        ↓
Script runs top to bottom — UI renders
        ↓
User uploads PDF + pastes JD + clicks Analyse
        ↓
Script reruns — button returns True
        ↓
Validation checks pass
        ↓
st.spinner shows loading message
        ↓
tempfile saves PDF to disk temporarily
        ↓
analyze_resume(tmp_path, job_description) runs
        ↓
PDF reading → parsing → matching (20-30 seconds)
        ↓
result stored in st.session_state
        ↓
os.unlink deletes temporary file
        ↓
Script reruns — session_state has result
        ↓
Results section renders:
- Match score + progress bar
- Colour coded feedback
- Matched skills (green ticks)
- Missing skills (red crosses)
- Strengths (stars)
- Areas to improve (warnings)
- Recommendation (blue box)
- Collapsible parsed resume JSON

---

### WHAT WAS TESTED TODAY
Tested app.py with real resume:
File: Vaishali_Bhardwaj_ProductManager_AI.pdf
JD: Senior PM AI/ML at Meesho

Results displayed correctly:
- Match score: 72% with progress bar
- 12 matched skills shown with green ticks
- 7 missing skills shown with red crosses
- 3 strengths with star icons
- 3 areas to improve with warning icons
- Personalised recommendation in blue box
- Full parsed resume in collapsible section

---

### GENAI CONCEPTS DEMONSTRATED IN UI
The UI makes GenAI concepts visible to users:

Semantic matching → shown as specific matched skills
  not just keywords but meaning-based connections

Structured output → parsed resume displayed as JSON
  shows Claude extracted clean structured data

Chain of thought → recommendation shows reasoning
  not just a score but WHY and WHAT TO DO

LLM as expert → recommendation reads like a recruiter
  not generic advice but specific to this resume and JD

---

### DEBUGGING CHECKLIST FOR APP.PY

If app does not start:
□ Check (venv_ai) is active in terminal
□ Run: streamlit run app.py
□ Check port 8501 is not already in use

If file upload does not work:
□ Check uploaded_file is not None before processing
□ Check tempfile writes correctly to disk
□ Check os.unlink runs after analysis completes

If results disappear after clicking:
□ Check st.session_state stores result correctly
□ Check session_state keys match exactly everywhere

If analysis fails silently:
□ Check "error" key in result dictionary
□ Add print statements to track where failure occurs

If spinner never disappears:
□ Check for errors inside the with st.spinner block
□ Any exception inside stops the spinner incorrectly


## Day 6 - Conversational Chat Agent
### Files : agent/career_coach.py and app.py (updated)

### WHY THIS EXISTS
The analysis result is a one-way output — user sees score and gaps.
The chat agent turns it into a two-way conversation.
User can ask follow up questions, request rewrites, get advice.
No competitor has this. This is the differentiator.

### THE KEY CONCEPT — HOW LLM MEMORY WORKS
Claude has NO memory between API calls.
Every call is completely fresh — Claude remembers nothing.

So how do chatbots remember?
Answer: you send the ENTIRE conversation history every call.

Call 1: [User: "What are my gaps?"]
Call 2: [User: "What are my gaps?", AI: "Missing PRD...", User: "How do I fix it?"]
Call 3: [ALL previous messages PLUS new message]

Every call includes full history.
Claude reads it all and responds with complete context.
LangChain's ChatMessageHistory automates this list management.

### THREE FILES AND THEIR JOBS

build_system_prompt() — creates the briefing document
Takes parsed_resume, job_description, match_result as input.
Builds a detailed f-string prompt containing:
- Candidate's name, skills, experience, certifications
- Full job description
- Match score, matched skills, missing skills
- Strengths and gaps from analysis
- 7 behaviour rules for the career coach persona
This is injected ONCE before conversation starts.
Claude knows everything before user asks first question.

build_career_coach() — assembles the agent
Creates the prompt template with three parts:
1. SystemMessage — the briefing document (injected once)
2. MessagesPlaceholder — where conversation history goes
3. Human message — the current user input

Creates ChatMessageHistory — the in-memory message store.
Wraps chain with RunnableWithMessageHistory — adds auto memory.
Returns both agent and history objects.

chat_with_coach() — sends one message
Called every time user sends a message.
Invokes the agent with the user's text.
Memory is handled automatically.
Returns Claude's response as plain string.


### NEW LANGCHAIN CONCEPTS

MessagesPlaceholder:
Special placeholder in ChatPromptTemplate.
LangChain fills it with full conversation history automatically.
Without it — Claude forgets every previous message.
With it — Claude sees entire conversation every call.

RunnableWithMessageHistory:
Modern LangChain way to add memory to any chain.
Wraps your chain with automatic history management.
Reads history before each call.
Saves response to history after each call.
You never manually manage the message list.

ChatMessageHistory:
Simple in-memory list of HumanMessage and AIMessage objects.
Grows with every exchange.
Gets inserted into MessagesPlaceholder on every call.

lambda session_id: message_history:
A tiny anonymous function.
Returns the message history for any session_id.
Allows multiple users to have separate histories in production.

### THE CRITICAL STREAMLIT BUG WE FIXED

Bug: Results and chat were indented INSIDE the button block.
Effect: When user typed in chat, button was not clicked,
entire block was skipped, results and chat disappeared.

Wrong structure:
if analyse_button:          ← button block
    run analysis
    if analysis_done:       ← INSIDE button block — wrong
        show results
    if analysis_done:       ← INSIDE button block — wrong
        show chat

Correct structure:
if analyse_button:          ← button block only
    run analysis

if analysis_done:           ← ROOT level — always runs
    show results

if analysis_done:           ← ROOT level — always runs
    show chat

Lesson: In Streamlit, anything that should persist across
reruns must be at root level — not inside button blocks.
Only the analysis logic belongs inside the button block.

### SESSION STATE KEYS USED

analysis_done: True/False — whether analysis has run
result: the complete pipeline output dictionary
job_description: the job description text
agent: the RunnableWithMessageHistory object
history: the ChatMessageHistory object
messages: list of {role, content} dicts for display

### GENAI CONCEPTS IN THIS FILE

Context injection     → system prompt contains full resume analysis
Memory               → ChatMessageHistory + MessagesPlaceholder
Multi-turn dialogue  → full history sent on every API call
Persona prompting    → expert career coach with 15 years experience
Behavioural rules    → 7 specific instructions shape every response
Session persistence  → st.session_state keeps agent alive across reruns


## LangSmith Observability — Added Day 7

### What it is
LangSmith is LangChain's observability platform.
Every chain run, every API call, every token is tracked
and visualised in a real-time dashboard.

### What it shows
- Every step of every chain execution
- Exact prompt sent to Claude
- Exact response received from Claude
- Token count per call
- Latency per step
- Error tracking with full context

### How it was set up
Three environment variables added to .env:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-ai-coach
LANGCHAIN_API_KEY=your_key

No code changes needed.
LangChain detects these variables automatically.

### Why it matters for the product
Observability is how you debug AI systems in production.
When output quality drops, you open LangSmith and see
exactly what prompt produced the bad output.
When latency spikes, you see which step is slow.
This is what real AI engineering teams use daily.

### What you can see in the trace
Left panel: chain breakdown
  RunnableSequence
    claude-sonnet-4-6 (time + tokens)
    JsonOutputParser (time)

Right panel:
  Input tab: exact resume text sent to Claude
  Output tab: exact structured JSON returned
  Metadata tab: model, tokens, latency details

### Interview talking point
"I added LangSmith observability to my project.
Every chain run is traced — I can see the exact prompt,
response, token count, and latency for every API call.
This is how production AI teams debug and monitor
LLM applications. It also visually proves my app
uses a real multi-step chain, not just a single API call."
```

Press `Cmd + S`.

---

## What LangSmith shows about your app architecture

Look at what the trace revealed:
```
claude-sonnet-4-6: 13.36 seconds, 1.9K tokens
JsonOutputParser:  0.00 seconds


## Day 7 — LangSmith Observability + RAG Knowledge Base
### Files: vectorstore/knowledge_base.py, vectorstore/embedder.py
### Updated: agent/career_coach.py

---

### LANGSMITH OBSERVABILITY

WHAT IT IS:
LangChain's observability platform.
Tracks every chain run, every API call, every token.
Visualises the complete pipeline in a dashboard.

HOW IT WAS SET UP:
Three environment variables added to .env:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-ai-coach
LANGCHAIN_API_KEY=your_key_here

No code changes needed.
LangChain automatically detects and sends traces.

WHAT YOU CAN SEE IN LANGSMITH:
- Every step of every chain execution
- Exact prompt sent to Claude
- Exact response received
- Token count per API call
- Latency per step in milliseconds
- Error context when things fail

WHY IT MATTERS:
Observability is how production AI teams debug and monitor.
When output quality drops you see exactly what prompt caused it.
When latency spikes you see which step is slow.
Screenshot of LangSmith trace is strong portfolio evidence.

INTERVIEW ANSWER:
"I added LangSmith observability so every chain run is fully
traced. I can see the exact prompt, response, token count,
and latency for every API call. This is how production AI
teams monitor LLM applications and debug quality issues."

---

### RAG — RETRIEVAL AUGMENTED GENERATION

WHY RAG WAS ADDED:
Without RAG, Claude answers from general training data.
Good but generic. May hallucinate specific details.
With RAG, Claude answers from YOUR specific knowledge base.
Grounded, specific, expert-level responses.

THE THREE NEW CONCEPTS:

1. EMBEDDINGS
Converting text to vectors — lists of numbers representing meaning.
Similar meanings produce similar vectors.
"STAR method" and "bullet point framework" are close vectors.
"STAR method" and "cooking recipe" are far apart vectors.
Model used: sentence-transformers/all-MiniLM-L6-v2
Why this model: free, runs locally, no API cost, industry standard.

2. VECTOR STORE (FAISS)
Database that stores vectors and finds similar ones fast.
FAISS = Facebook AI Similarity Search.
Runs locally — no server, no cost, no API needed.
Saves to disk as faiss_index/ folder.
Built once, loaded on every subsequent app start.

3. TEXT SPLITTERS
Large documents split into smaller chunks before embedding.
Why: a 2000 word document as one vector is too general.
Split into 10 chunks of 200 words — each chunk is specific.
chunk_size=500: each chunk maximum 500 characters.
chunk_overlap=50: adjacent chunks share 50 characters.
Overlap ensures sentences at boundaries are never lost.
Class used: RecursiveCharacterTextSplitter
Splits at: paragraph breaks → line breaks → sentences → words

THE RAG PIPELINE:

PREPARATION (done once, saved to disk):
12 knowledge base documents written
        ↓
RecursiveCharacterTextSplitter creates 29 chunks
        ↓
all-MiniLM-L6-v2 converts each chunk to a vector
        ↓
FAISS stores all vectors in faiss_index/ folder

AT QUERY TIME (every user question):
User asks question
        ↓
Question converted to vector by same embedding model
        ↓
FAISS finds 3 most similar chunks (similarity_search)
        ↓
3 chunks joined into one string
        ↓
String injected into Claude's prompt as [KNOWLEDGE BASE]
        ↓
Claude answers from retrieved expertise not hallucination

THE KNOWLEDGE BASE CONTENTS:
1. Strong bullet points — STAR method
2. Quantifying achievements
3. Resume structure for PM roles
4. What AI PM roles look for in 2026
5. How to showcase LLM experience
6. PRD writing for AI features
7. ATS optimisation rules for 2026
8. Keywords for AI PM roles
9. What Indian tech companies look for
10. Framing enterprise experience for consumer tech
11. Top AI PM interview questions
12. Salary context for AI PM roles in India

HOW RAG CONNECTS TO CHAT AGENT:
In chat_with_coach() function:
1. User message received
2. retrieve_relevant_knowledge(user_message) called
3. Top 3 relevant chunks retrieved from FAISS
4. Enhanced message built:
   Original question + retrieved knowledge chunks
5. Enhanced message sent to Claude via agent
6. Claude answers grounded in retrieved expertise

DIFFERENCE FROM CONTEXT INJECTION:
Context injection: fixed data injected once per session
   (resume + JD + analysis results — same every call)

RAG: dynamic retrieval at every query
   (different chunks retrieved for different questions)
   "bullet points question" → retrieves STAR method chunk
   "ATS score question" → retrieves ATS optimisation chunk
   "interview question" → retrieves interview prep chunk

Both work together in this app.

WHAT STAR METHOD IS:
Storytelling framework for resume bullets and interviews.
S — Situation: what was the context?
T — Task: what was your responsibility?
A — Action: what did YOU specifically do?
R — Result: what was the measurable outcome?

Weak bullet: "Worked on AI projects"
Strong bullet: "Defined requirements for Vertex AI integration
               partnering with 4 ML engineers across 3 sprints,
               reducing manual reporting effort by 25%"

STAR forces specificity, quantification, and attribution.
Every resume bullet should follow this structure.

DEBUGGING CHECKLIST:
If vector store not found:
□ Run: python vectorstore/embedder.py to rebuild
□ Check faiss_index/ folder exists in vectorstore/

If retrieval returns irrelevant results:
□ Check knowledge_base.py documents are relevant
□ Try increasing k from 3 to 5 in retrieve_relevant_knowledge
□ Add more specific documents to knowledge base

If import error on career_coach.py:
□ Check: from vectorstore.embedder import retrieve_relevant_knowledge
□ Run from project root, not from inside a subfolder

GENAI CONCEPTS IN RAG:
Embeddings          → text converted to semantic vectors
Vector similarity   → finding meaning-close chunks
Retrieval           → dynamic knowledge at query time
Grounding           → answers from facts not hallucination
Chunking            → splitting docs for precise retrieval
Semantic search     → meaning-based not keyword-based


## Day 7 — Cover Letter Generator
### File: chains/cover_letter.py
### Updated: app.py

---

### WHY THIS FILE EXISTS
After seeing their match analysis, users need help
applying to the job. A tailored cover letter is the
next logical step. Generic cover letters get ignored.
This generates a specific letter using everything
the app already knows about the user and the role.

---

### WHAT IS NEW COMPARED TO PREVIOUS CHAINS

Previous chains returned JSON:
resume_parser_chain = prompt | llm | JsonOutputParser
jd_matcher_chain = prompt | llm | JsonOutputParser

This chain returns plain text:
cover_letter_chain = prompt | llm | StrOutputParser

StrOutputParser vs JsonOutputParser:
JsonOutputParser — extracts JSON, returns Python dictionary
StrOutputParser — returns raw text string as-is
Cover letter is prose text not structured data.
So StrOutputParser is the correct choice here.

---

### THE PROMPT ENGINEERING IN THIS FILE

Four techniques working together:

1. ROLE PROMPTING
"You are an expert cover letter writer with 15 years
of experience helping professionals land senior roles
at top tech companies."
Activates specific cover letter writing expertise.

2. NEGATIVE CONSTRAINTS — what NOT to do
"You never use clichés like:
- I am writing to apply for...
- I am a passionate and driven professional...
- I would be a great fit because..."
Explicitly forbidding bad patterns is as important
as instructing good ones. Without this, Claude
defaults to template-sounding language.

3. CONTEXT INJECTION — all analysis results passed in
Name, recent role, skills, certifications,
job description, match score, strengths, gaps,
recommendation — all injected as variables.
Every letter is specific to this person and this job.

4. STRUCTURAL INSTRUCTIONS — paragraph by paragraph
Paragraph 1: open with strongest achievement
Paragraph 2: connect AI experience to company
Paragraph 3: address gap honestly and reframe
Closing: specific ask with confident tone
Telling Claude the structure produces consistent,
well-organised letters every time.

---

### THE VARIABLES IN THIS CHAIN

cover_letter_chain.invoke({
    "name": name,
    "recent_role": recent_role,
    "recent_company": recent_company,
    "skills": ", ".join(skills[:10]),
    "certifications": certifications,
    "years_experience": years_experience,
    "job_description": job_description,
    "match_score": match_score,
    "strengths": strengths,
    "gaps": gaps,
    "recommendation": recommendation
})

skills[:10] — only first 10 skills passed.
Why: listing all 28 skills in a cover letter is
overwhelming. First 10 are most important.

years_experience = len(experience) * 2
Why: rough estimate assuming 2 years per role.
Not perfect but reasonable for a cover letter.

---

### HOW IT CONNECTS TO UI (app.py)

Button triggers generation:
if st.button("Generate Cover Letter", type="secondary"):
    cover_letter = generate_cover_letter(
        result["parsed_resume"],
        st.session_state["job_description"],
        result["match_result"]
    )
    st.session_state["cover_letter"] = cover_letter

Stored in session_state so it survives reruns.

Displayed in text area:
st.text_area("Your Cover Letter",
             value=st.session_state["cover_letter"],
             height=400)

User can select all and copy directly from the text area.

---

### WHAT MAKES THE GENERATED LETTER STRONG

The gap reframing is the most valuable part.
Most candidates either ignore their gaps or apologise.
This chain addresses gaps directly and reframes them
as perspective advantages.

Example from real output:
Gap: No ecommerce experience
Reframe: "I've built AI products where a single model
failure means network degradation affecting millions
of critical connections. That instils a rigour around
model evaluation that consumer internet sometimes skips."

This is genuine career coaching — not just filling a template.

---

### GENAI CONCEPTS IN THIS FILE

Prompt Engineering    → role, constraints, structure, context
Role Prompting        → expert cover letter writer persona
Negative Constraints  → explicitly forbidding clichés
Context Injection     → all analysis results as variables
Structural Prompting  → paragraph-by-paragraph instructions
StrOutputParser       → plain text output not JSON
Multi-variable LCEL   → 11 variables in one invoke call

---

### DEBUGGING CHECKLIST

If letter sounds generic:
□ Check all variables are being passed to invoke()
□ Check job_description is in session_state
□ Check match_result has strengths and gaps populated

If letter is too long:
□ Add to system_message: "Maximum 350 words strictly"

If gap reframing is weak:
□ Add more specific reframing examples to human_message
□ Tell Claude: "The reframe must be specific to their
  actual experience, not a generic statement"

If StrOutputParser not found:
□ from langchain_core.output_parsers import StrOutputParser


## Day 8 — PDF Export Features + Enhanced Resume Download
### Files: tools/pdf_exporter.py, chains/bullet_extractor.py,
### chains/resume_enhancer.py, app.py (updated)

---

### THREE NEW FILES CREATED

1. tools/pdf_exporter.py
   Two functions:
   create_resume_pdf() — formats parsed resume as PDF
   create_analysis_report() — formats match analysis as PDF

2. chains/bullet_extractor.py
   Extracts bullet points from conversational agent responses
   Uses Claude to identify and clean bullet text
   Returns a Python list of clean bullet strings

3. chains/resume_enhancer.py
   Scans chat history for rewritten bullets
   Matches bullets to the correct job using word scoring
   Replaces original bullets with improved ones
   Returns enhanced resume dictionary

---

### WHAT REPORTLAB IS

Python library for generating PDF files programmatically.
You write Python code that places elements on a page.
reportlab handles layout, fonts, colours, page breaks.

Key concept — FLOWABLES:
Elements that flow down the page one after another.
You build a list called story and append flowables.
doc.build(story) places them on the page in order.

Five flowables used:
Paragraph(text, style) — text block with formatting
Spacer(width, height)  — invisible gap between elements
HRFlowable(...)        — horizontal divider line
SimpleDocTemplate      — the document itself

ParagraphStyle:
Named set of formatting rules.
fontSize, fontName, textColor, alignment, spaceAfter.
Define once, apply to any Paragraph.
parent=styles["Normal"] inherits base settings.

---

### TWO PDF OUTPUTS

OUTPUT 1 — Analysis Report
Contains:
- Title: AI Resume Analysis Report
- Prepared for: candidate name
- Role: first line of job description
- Match score as large centred number (28pt font)
- Colour coded verdict (green/amber/red)
- Matched skills in green
- Missing skills in red
- Strengths numbered list
- Gaps numbered list
- Recommendation paragraph
- Cover letter if generated (page 2)

Why this is valuable:
User gets a document they cannot get anywhere else.
Printable, shareable, usable as application checklist.
Cover letter included so entire application in one PDF.

OUTPUT 2 — Enhanced Resume
Contains:
- Same structure as original resume
- BUT with AI-improved bullet points replacing originals
- Only the sections rewritten in chat are changed
- Original sections preserved exactly

Why this is valuable:
User goes from old resume to tailored resume in one session.
No manual copying. App does it automatically.
Enhanced bullets are specific to the target job.

---

### HOW BULLET EXTRACTION WORKS

Problem:
Agent responses are conversational — mixed with
explanations, tables, emojis, before/after examples.
Cannot simply look for lines starting with bullet symbols.
Need Claude to identify which lines are the actual bullets.

Solution: bullet_extractor_chain
Sends the full agent response to Claude.
Asks: extract only the bullet points, return as JSON.
Returns: {"bullets": ["bullet 1", "bullet 2", ...]}

Why use Claude for extraction:
Rule-based extraction fails on rich formatted text.
Claude understands meaning — knows a bullet from an
explanation even without consistent formatting symbols.

---

### HOW RESUME ENHANCEMENT WORKS

enhance_resume_with_chat() steps:

1. copy.deepcopy(parsed_resume)
   Creates completely independent copy.
   Changes to copy do not affect original.
   Critical — we never modify the original resume.

2. Filter assistant messages only
   User messages never contain bullets.
   Only scan Claude's responses.

3. Quick signal check before API call
   Check for: bullet symbols, "rewritten", "improved"
   Skip messages without these signals.
   Saves API credits — only call extractor when needed.

4. Extract bullets from matching messages
   Call extract_bullets_from_text() on signal messages.
   Returns list of clean bullet strings.

5. Find best matching job by word score
   For each job in experience:
   Count how many words from company+role appear in message.
   Job with highest score gets the new bullets.
   Example: message mentions "BT Group" and "Openreach"
   → BT Group job gets highest score → bullets replaced.

6. Mark job as enhanced
   Add "enhanced": True flag to modified jobs.
   Used by get_enhancement_summary() to report changes.

---

### THE DEEP COPY CONCEPT

Shallow copy:
enhanced = parsed_resume
Both variables point to SAME object in memory.
Change enhanced → changes parsed_resume too.
Original is destroyed.

Deep copy:
enhanced = copy.deepcopy(parsed_resume)
Creates completely new object with new nested objects.
Change enhanced → parsed_resume unchanged.
Original is preserved.

Always use deep copy when modifying a dictionary
that you want to keep the original version of.

---

### APP.PY STRUCTURE — FINAL CLEAN VERSION

Four root-level blocks:

Block 1: Button logic
if analyse_button and not session_state("analysis_done"):
    run analysis, save to session_state

Block 2: Results section
if session_state("analysis_done"):
    show score, skills, recommendation
    cover letter generator
    analysis report download

Block 3: Chat section
if session_state("analysis_done"):
    build agent if not exists
    display chat history
    handle new messages

Block 4: Enhanced resume download
if session_state("analysis_done"):
    check for coaching responses in chat
    generate enhanced resume
    download button

Key lesson:
Results, chat, and download are all ROOT LEVEL blocks.
None of them are nested inside the button block.
This is why they persist across reruns.

---

### COMPLETE USER JOURNEY — V2

Upload PDF resume
        ↓
Paste job description
        ↓
Click Analyse (20-30 seconds)
        ↓
See: match score, matched/missing skills,
     strengths, gaps, recommendation
        ↓
Generate cover letter (optional)
        ↓
Download analysis report PDF (optional)
        ↓
Chat with AI career coach:
- Ask about missing skills
- Request bullet rewrites
- Get specific advice
        ↓
Download enhanced resume PDF
(with AI-improved bullets automatically applied)
        ↓
Apply for job with everything optimised

---

### GENAI CONCEPTS IN THESE FILES

StrOutputParser     → plain text output for cover letter
JsonOutputParser    → structured JSON for bullet extraction
Deep copy           → safe dictionary manipulation
Word scoring        → simple matching algorithm without ML
Negative constraints→ telling Claude what NOT to write
Structural prompting→ paragraph-by-paragraph instructions
Context injection   → full analysis injected into every call