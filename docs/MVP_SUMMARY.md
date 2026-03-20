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
