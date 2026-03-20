What the app does in one sentence
A user uploads their PDF resume, pastes a job description, gets an AI-powered match analysis with score and gaps, then has a conversation with an AI career coach that remembers their full profile and gives personalised advice.

The Tech Stack — what and why
LANGUAGE:        Python
WHY:             Entire AI/ML ecosystem is Python-first.
                 LangChain, Anthropic SDK, pdfplumber — 
                 all Python native.

LLM:             Claude Sonnet (claude-sonnet-4-6) by Anthropic
WHY:             200,000 token context window vs GPT-4o's 128,000.
                 Full resume + JD + chat history fits in one call.
                 Better structured JSON extraction than alternatives.
                 Cost efficient — more capable than Haiku,
                 more affordable than Opus.

FRAMEWORK:       LangChain
WHY:             Provides chains, memory, agents, tools out of the box.
                 Model agnostic — can swap Claude for any LLM.
                 LangSmith observability built in.
                 Industry standard for production LLM applications.

UI:              Streamlit
WHY:             Python-only — no HTML, CSS, JavaScript needed.
                 Built-in file uploader, chat interface, progress bars.
                 Deploys to Streamlit Cloud in minutes.
                 Industry standard for AI demos and prototypes.

PDF PARSING:     pdfplumber
WHY:             Best at handling resume-specific layouts —
                 columns, tables, custom fonts.
                 Handles multi-page documents automatically.

API SECURITY:    python-dotenv + .env file
WHY:             API keys never hardcoded in source code.
                 .gitignore prevents .env from going to GitHub.
                 Industry standard security practice.

The Folder Structure — what lives where and why
resume-ai-coach/
│
├── app.py                 THE FACE
│                          Streamlit UI. Everything the user sees.
│                          Calls pipeline and agent. Manages session.
│
├── pipeline.py            THE COORDINATOR
│                          Orchestration layer.
│                          Connects pdf_reader → parser → matcher.
│                          One function call runs everything.
│
├── chains/
│   ├── resume_parser.py   BRAIN PIECE 1
│   │                      Text → structured JSON.
│   │                      Uses: PromptTemplate, Claude, JsonOutputParser
│   │
│   └── jd_matcher.py      BRAIN PIECE 2
│                          Resume + JD → match analysis.
│                          Uses: two variables, chain of thought prompting
│
├── tools/
│   └── pdf_reader.py      THE EYES
│                          PDF file → clean plain text.
│                          Handles encoding issues (cid:127).
│                          Has @tool version for agent use.
│
├── agent/
│   └── career_coach.py    THE CONVERSATIONALIST
│                          Builds chat agent with full context.
│                          Manages conversation memory.
│                          Answers follow-up questions.
│
└── docs/
    └── DECISIONS.md       THE BRAIN RECORD
                           Every technical decision documented.
                           What was used, why, trade-offs considered.

The Data Flow — what happens step by step
USER ACTION: uploads PDF + pastes JD + clicks Analyse
                    ↓
app.py receives uploaded file (in memory, no file path yet)
                    ↓
tempfile creates temporary PDF on disk → gives real file path
                    ↓
pipeline.py: analyze_resume(pdf_path, job_description)
                    ↓
    STEP 1: tools/pdf_reader.py
            pdfplumber opens PDF
            loops through every page
            extracts text
            clean_text() fixes (cid:127) encoding issues
            returns clean plain text string
                    ↓
    STEP 2: chains/resume_parser.py
            ChatPromptTemplate fills {resume_text} placeholder
            Claude reads resume text
            Returns structured JSON
            JsonOutputParser converts to Python dictionary
            Returns: {name, email, skills, experience, education}
                    ↓
    STEP 3: chains/jd_matcher.py
            ChatPromptTemplate fills {resume_text} AND {job_description}
            Claude compares both semantically
            Returns match analysis JSON
            Returns: {score, matched_skills, missing_skills,
                      strengths, gaps, recommendation}
                    ↓
pipeline.py returns: {parsed_resume, match_result}
                    ↓
app.py stores everything in st.session_state
                    ↓
app.py displays results:
- match score + progress bar
- matched skills (green ticks)
- missing skills (red crosses)
- strengths (stars)
- gaps (warnings)
- recommendation (blue box)
- parsed resume JSON (collapsible)

USER ACTION: types question in chat box
                    ↓
agent/career_coach.py: chat_with_coach(agent, user_message)
                    ↓
RunnableWithMessageHistory reads full conversation history
                    ↓
Prompt built with three parts:
1. SystemMessage: full resume + JD + analysis injected
2. MessagesPlaceholder: entire conversation history
3. Human message: current question
                    ↓
Claude reads all three parts → generates personalised response
                    ↓
Response saved to ChatMessageHistory
                    ↓
app.py displays response as chat bubble
                    ↓
User can keep asking — memory grows with every exchange

The 7 GenAI Concepts — name, definition, where used
Concept 1 — Prompt Engineering
Deliberately designing instructions to get consistent, reliable LLM outputs.
Used in every file. Not just asking questions — structured instructions with specific techniques.
Concept 2 — Role Prompting
Giving the LLM a specific expert persona before any task.
resume_parser.py: "You are an expert resume parser"
jd_matcher.py:   "You are an expert recruitment consultant
                  with 15 years of experience"
career_coach.py: "You are an expert AI career coach
                  with 15 years of experience"
Why it works: Claude was trained on billions of documents including text written by these experts. The role activates that specific knowledge domain.
Concept 3 — Output Constraints
Explicitly telling the LLM what format to return and forbidding everything else.
"Return valid JSON only.
No extra text. No explanation. No markdown.
Just the raw JSON object."
Why it matters: Without constraints Claude adds conversational text that breaks the JsonOutputParser.
Concept 4 — Chain of Thought Prompting
Forcing the LLM to reason step by step before giving a final answer.
Used in jd_matcher.py:
Analyse carefully:
1. Which skills does the candidate have?
2. Which are missing?
3. What are their strengths?
4. What are the gaps?
5. Overall fit?
Why it works: LLMs give more accurate answers when guided to think through each dimension rather than jumping to a conclusion.
Concept 5 — LangChain Chains (LCEL)
Connecting components in sequence using the pipe operator.
resume_parser_chain = prompt | llm | parser
jd_matcher_chain   = prompt | llm | parser
Each component receives the output of the previous one as input. Fixed sequence. Deterministic. Same input always follows the same path.
Concept 6 — Context Injection
Injecting specific information into the LLM's context before a conversation begins so it knows everything without the user having to explain.
Used in career_coach.py system prompt:
Name: Vaishali Bhardwaj
Match Score: 72%
Missing Skills: PRD writing, ecommerce experience
Full resume text + job description + analysis results
Why it matters: Makes every coaching response personalised to THIS user's specific situation. Not generic advice.
Concept 7 — Conversation Memory
Storing the full conversation history and sending it with every API call so the LLM appears to remember.
LLMs are stateless — every API call is completely fresh.
Memory is the pattern of: store every exchange →
send full history with every new message →
Claude reads everything → responds with full context.
Tools used: ChatMessageHistory stores messages. MessagesPlaceholder inserts them into the prompt. RunnableWithMessageHistory automates both.

Semantic Understanding — your competitive advantage
Keyword matching (what competitors like Jobscan do):
Checks if exact words from JD appear in resume.
JD says:     "payments infrastructure"
Resume says: "payment integration project"
Result:      NOT MATCHED — words are different
Semantic understanding (what Claude does):
Compares meaning and context, not words.
JD says:     "payments infrastructure"
Resume says: "payment integration project"
Result:      MATCHED — same domain, same type of work
Why this is better: Claude was trained on billions of documents. Every word was converted to a vector — a list of numbers representing its meaning. Similar meanings have similar vectors. Claude compares meaning coordinates, not word strings.
Interview line: "Unlike keyword matching tools that check for exact word presence, our app uses Claude's semantic understanding to compare meaning and context — the same way a human recruiter reads a resume."

Key Decisions and Why — for your notebook
Decision 1: Claude Sonnet not Opus
Reason: 5x cheaper than Opus. Sonnet has sufficient
capability for resume parsing and matching.
PM principle: cheapest model that meets quality requirements.

Decision 2: Claude Sonnet not Haiku
Reason: Haiku produced inconsistent JSON on complex resumes.
Quality is non-negotiable for a user-facing product.

Decision 3: Claude Sonnet not GPT-4o
Reason: 200k vs 128k context window.
Simpler architecture — no memory compression needed.
Better structured extraction performance.

Decision 4: LangChain not raw Anthropic SDK
Reason: SDK only does send/receive.
LangChain adds chains, memory, agents, tools, observability.
Building all that from scratch = weeks of work.

Decision 5: pipeline.py as separate orchestration layer
Reason: app.py should only handle UI.
Separating concerns means UI can change without touching logic.
Same pipeline could serve a mobile app or Chrome extension.

Decision 6: Streamlit not Flask or React
Reason: Python-only. No frontend expertise needed.
Fast to build. Looks professional enough for a demo.
Can be replaced with React later without changing backend.

Decision 7: tempfile for PDF handling
Reason: Streamlit holds uploaded files in memory.
pdfplumber needs a real file path on disk.
tempfile bridges the gap. Cleans up automatically.

Decision 8: session_state for persistence
Reason: Streamlit reruns entire script on every interaction.
Without session_state, results disappear on every rerun.
session_state is Streamlit's persistent dictionary across reruns.

The Three Things That Make This App Different
Write these in your notebook. Say them out loud until they feel natural.
Differentiator 1 — Semantic matching not keyword matching
Other tools count keyword matches. Your app understands meaning. Claude connected "payment integration project" to "payments infrastructure" without those exact words appearing in both places.
Differentiator 2 — Genuine recommendation not just a score
Every competitor gives a percentage. Your app gives a specific, personalised recommendation written the way a real career coach would write it — referencing actual companies, actual metrics, actual gaps.
Differentiator 3 — Conversational memory
No competitor has a chat agent that remembers the full resume, the job description, the analysis, and the entire conversation. When you ask "make that shorter" — the agent knows what it just wrote and shortens it. Multi-turn conversation with full context.

The One Paragraph to Memorise
Read this out loud three times. Then close this and say it in your own words.
"I built an AI Resume Coach using LangChain and Claude's API. The app reads a PDF resume, extracts structured data using a parsing chain, compares it against a job description using Claude's semantic understanding — not keyword matching — and returns a match score with specific gaps and a personalised recommendation. What makes it genuinely different is the conversational career coach built on top. After the analysis, users can have a full conversation — the agent knows their complete resume, the job description, the match results, and remembers everything said in the session. I built it because I was facing this problem personally, and the tools available were giving me ATS scores but no real guidance. Every technical decision was deliberate — Claude Sonnet for the 200k context window, LangChain for orchestration, separate pipeline and UI layers for clean architecture."


# AI Resume Coach — V1 MVP Reference
# Author: Vaishali Bhardwaj
# Version: 1.0 | Built: March 2026

---

## What This App Does — One Paragraph

An AI-powered resume coach that reads a PDF resume,
extracts structured data, compares it against a job
description using semantic understanding, and returns
a match score with specific gaps and personalised
recommendation. A conversational chat agent with full
memory then lets the user ask follow-up questions,
request rewrites, and get specific career advice —
all grounded in their actual resume and job description.

---

## The Problem It Solves

Existing tools like Jobscan give ATS keyword scores.
They do not give genuine advice.
They cannot answer follow-up questions.
They use keyword matching — not semantic understanding.
This app was built from personal experience of that gap.

---

## Tech Stack — What and Why

| Technology | What | Why |
|---|---|---|
| Python | Language | AI/ML ecosystem is Python-first |
| Claude Sonnet | LLM | 200k token window, best JSON extraction |
| LangChain | Framework | Chains, memory, agents out of the box |
| Streamlit | UI | Python-only, built-in file upload and chat |
| pdfplumber | PDF reader | Best for resume layouts and encoding |
| python-dotenv | Security | API keys never in source code |
| tempfile | Bridge | Connects Streamlit memory to disk |
| FAISS (planned) | Vector DB | RAG knowledge base — Week 3 roadmap |

---

## Folder Structure — What Lives Where

## Folder Structure — What Lives Where
```
resume-ai-coach/
├── app.py                 UI layer — what user sees
├── pipeline.py            Orchestration — connects everything
├── chains/
│   ├── resume_parser.py   Text → structured JSON
│   └── jd_matcher.py      Resume + JD → match analysis
├── tools/
│   └── pdf_reader.py      PDF → clean text
├── agent/
│   └── career_coach.py    Conversational AI with memory
└── docs/
    ├── DECISIONS.md        Full detailed documentation
    ├── MVP_SUMMARY.md      This file — quick reference
    └── ARCHITECTURE.md     Architecture diagrams
```

---

## The Data Flow — Step by Step
```
User uploads PDF + pastes JD + clicks Analyse
        ↓
tempfile saves PDF to disk (bridge from memory to disk)
        ↓
pipeline.py: analyze_resume(pdf_path, job_description)
        ↓
Step 1: pdf_reader.py
        pdfplumber extracts text from every page
        clean_text() fixes (cid:127) encoding issues
        Returns: clean plain text string
        ↓
Step 2: resume_parser.py
        PromptTemplate fills {resume_text}
        Claude extracts structured data
        JsonOutputParser converts to dictionary
        Returns: {name, email, skills, experience, education}
        ↓
Step 3: jd_matcher.py
        PromptTemplate fills {resume_text} + {job_description}
        Claude compares both semantically
        Returns: {score, matched_skills, missing_skills,
                  strengths, gaps, recommendation}
        ↓
app.py stores in session_state
app.py displays results

User types in chat box
        ↓
career_coach.py: chat_with_coach(agent, message)
        ↓
RunnableWithMessageHistory reads full history
        ↓
Prompt = SystemMessage (full context) +
         MessagesPlaceholder (full history) +
         Human message (current question)
        ↓
Claude responds with full personalised context
        ↓
Response saved to ChatMessageHistory
        ↓
Chat bubble displayed in UI
```

---

## 7 GenAI Concepts — Name, Definition, Where Used

### 1. Prompt Engineering
Deliberately designing LLM instructions to get
consistent, reliable outputs every time.
Used in every file in this project.

### 2. Role Prompting
Giving Claude a specific expert persona.
```
resume_parser.py:  "You are an expert resume parser"
jd_matcher.py:     "You are an expert recruitment consultant
                    with 15 years of experience"
career_coach.py:   "You are an expert AI career coach"
```
Why: activates specific expert knowledge from training data.

### 3. Output Constraints
Telling Claude exactly what format to return.
```
"Return valid JSON only.
No extra text. No explanation. No markdown."
```
Why: without this Claude adds text that breaks JsonOutputParser.

### 4. Chain of Thought Prompting
Forcing Claude to reason step by step before answering.
Used in jd_matcher.py:
```
Analyse carefully:
1. Which skills does the candidate have?
2. Which are missing?
3. What are their strengths?
4. What are the gaps?
5. Overall fit?
```
Why: step-by-step reasoning produces more accurate results
than asking for the conclusion directly.

### 5. LangChain Chains (LCEL)
Connecting components in sequence using pipe operator.
```
chain = prompt | llm | parser
```
Output of each component flows into the next.
Fixed sequence. Deterministic. Used in parser and matcher.

### 6. Context Injection
Injecting full analysis into system prompt before chat.
```
System prompt contains:
- Full resume text
- Job description
- Match score, matched skills, missing skills
- Strengths and gaps
- 7 behaviour rules
```
Why: every chat response is personalised to THIS user.
Not generic career advice.

### 7. Conversation Memory
Storing full chat history and sending it every API call.
```
LLMs are stateless — every call is completely fresh.
Memory pattern:
store every exchange →
send full history with every new message →
Claude reads everything → responds with full context
```
Tools: ChatMessageHistory + MessagesPlaceholder +
       RunnableWithMessageHistory

---

## Semantic Understanding vs Keyword Matching

### Keyword Matching (Jobscan, basic ATS):
Checks if exact words from JD appear in resume.
```
JD:     "payments infrastructure"
Resume: "payment integration project"
Result: NOT MATCHED ❌ — words are different
```
Can be gamed by keyword stuffing.
No understanding of meaning or context.

### Semantic Understanding (Claude):
Compares meaning and context, not words.
```
JD:     "payments infrastructure"
Resume: "payment integration project"
Result: MATCHED ✅ — same domain, same work type
```
Claude connected "led team of 4" with "mentor junior engineers"
without those exact words appearing in both.

### Interview Line:
"Unlike keyword matching tools that check for exact word
presence, our app uses Claude's semantic understanding
to compare meaning and context — the same way a human
recruiter reads a resume."

---

## Key Technical Decisions and Why

### Claude Sonnet not Opus
5x cheaper. Sufficient capability for our tasks.
PM principle: cheapest model that meets quality requirements.

### Claude Sonnet not Haiku
Haiku produced inconsistent JSON on complex resumes.
Quality is non-negotiable for user-facing products.

### Claude Sonnet not GPT-4o
200k vs 128k context window.
Simpler architecture — no memory compression needed.
Better structured extraction performance in testing.

### LangChain not raw Anthropic SDK
Raw SDK: send text, get text back. That is all.
LangChain adds: chains, memory, agents, tools, observability.
Building from scratch = weeks of extra work.

### pipeline.py as separate orchestration layer
app.py handles only UI.
Separation of concerns — UI can change without touching logic.
Same pipeline could serve mobile app or Chrome extension later.

### Streamlit not Flask or React
Python-only — no frontend expertise needed.
Fast to build and demo.
Can be replaced with React later without changing backend.

### session_state for persistence
Streamlit reruns entire script on every user interaction.
Without session_state, results disappear on every rerun.
session_state is Streamlit's persistent dictionary.

---

## Three Differentiators — Say These in Every Interview

### 1. Semantic matching not keyword matching
Other tools count keyword matches.
This app understands meaning.
Claude connected "payment integration" with
"payments infrastructure" without exact word match.

### 2. Genuine recommendation not just a score
Every competitor gives a percentage.
This app gives a specific personalised recommendation
referencing actual companies, metrics, and gaps.
Sounds like a real recruiter wrote it.

### 3. Conversational memory
No competitor has a chat agent that remembers:
- The full resume
- The job description
- The complete match analysis
- Everything said in the conversation
When user says "make that shorter" — agent knows
exactly what it wrote and shortens it.
Multi-turn conversation with full persistent context.

---

## Concepts I Must Know for AI PM Interviews

### What is RAG?
Retrieval Augmented Generation.
Store knowledge base as vector embeddings.
At query time, retrieve most relevant documents.
Give them to LLM as context.
Reduces hallucination — model answers from your facts.
NOT what I built — I built context injection.
RAG is on my Week 3 roadmap using FAISS.

### What is a Vector / Embedding?
Every word converted to a list of numbers.
Similar meanings have similar numbers — close on a map.
"payments" and "financial transactions" are close.
"payments" and "cooking" are far apart.
This is why semantic search works.

### What is a Chain vs Agent?
Chain: fixed sequence. You decide the steps.
prompt | llm | parser — always in that order.

Agent: LLM decides the steps.
Give it tools and a goal.
It reasons about what to do next.
Your career coach behaves as an agent.

### What is Abstraction?
Hiding complexity behind a simple interface.
analyze_resume() hides PDF reading, parsing, matching.
UI just calls one function. Gets everything back.
Like a car pedal hiding the engine.

### What is Orchestration?
Coordinating multiple components to work together.
pipeline.py coordinates pdf_reader, parser, matcher.
Each component does one job.
Pipeline tells them when to run and combines results.
Like a restaurant coordinator connecting three chefs.

---

## Scalability Issues and Fixes — for Product Questions

| Problem | What breaks | Fix |
|---|---|---|
| API costs | $1,800/month at 1000 users/day | Rate limiting, auth, budget caps |
| Concurrent load | Streamlit single process | Migrate to FastAPI backend |
| Session state | Not production ready | Move to Redis |
| Processing speed | 20-30 seconds blocks server | Async processing with job IDs |
| No rate limiting | One user drains all credits | Per-user limits, authentication |

---

## The One Paragraph — Memorise This

"I built an AI Resume Coach using LangChain and Claude API.
The app reads a PDF resume, extracts structured data using
a parsing chain, compares it against a job description using
Claude's semantic understanding — not keyword matching —
and returns a match score with specific gaps and a
personalised recommendation. What makes it different is the
conversational career coach built on top. After analysis,
users can have a full conversation — the agent knows their
complete resume, the job description, the match results,
and remembers everything said in the session. I built it
because I was facing this problem personally. Every technical
decision was deliberate — Claude Sonnet for the 200k context
window, LangChain for orchestration, separate pipeline and
UI layers for clean architecture."

---

## Version 1 Completed Features

✅ PDF resume upload and text extraction
✅ Resume parsing to structured JSON
✅ JD matching with semantic understanding
✅ Match score with progress bar
✅ Matched and missing skills display
✅ Strengths and gaps analysis
✅ Personalised recommendation
✅ Conversational chat agent with memory
✅ Context injection before chat begins
✅ Multi-turn conversation with persistence
✅ Session state management
✅ Error handling throughout pipeline
✅ Full documentation in DECISIONS.md

## Version 2 Planned Features (Roadmap)

⏳ RAG knowledge base with FAISS
⏳ Live job listings via Adzuna API
⏳ Cover letter generator
⏳ PDF export of rewritten resume
⏳ LangSmith observability
⏳ FastAPI backend for production
⏳ Deployment to Streamlit Cloud