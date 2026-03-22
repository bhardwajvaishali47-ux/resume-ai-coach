# 📄 AI Resume Coach

> An AI-powered career coaching platform that analyses your resume against any job description, provides personalised match insights, and coaches you through improving your application — built with Claude AI, LangChain, and FastAPI.

---

## 🎯 The Problem

Job seekers spend hours tailoring resumes with no clear guidance on what actually matters for a specific role. Generic ATS tools give keyword scores but no real advice. There is no tool that tells you *exactly* how to position yourself for the role you want.

**AI Resume Coach solves this.**

---

## ✨ What Makes This Different

| Feature | Jobscan | Resume Worded | AI Resume Coach |
|---|---|---|---|
| Match Score | ✅ | ✅ | ✅ |
| Missing Skills | ✅ | ✅ | ✅ |
| Personalised Recommendation | ❌ | ❌ | ✅ |
| Conversational AI Coach | ❌ | ❌ | ✅ |
| Remembers Your Resume | ❌ | ❌ | ✅ |
| Rewrites Your Bullets | ❌ | ❌ | ✅ |
| Generates Cover Letter | ❌ | Limited | ✅ |
| Live Job Listings | ❌ | ❌ | ✅ |
| RAG Knowledge Base | ❌ | ❌ | ✅ |
| Download Enhanced Resume | ❌ | ❌ | ✅ |

---

## 🚀 Key Features

### 1. Resume Analysis
Upload your PDF resume and paste any job description. Get back:
- Match score (0-100%)
- Matched and missing skills
- Your strengths for this specific role
- Gaps a recruiter would flag
- A personalised recommendation written like a real career coach

### 2. Conversational AI Career Coach
After the analysis, chat with an AI coach that:
- Already knows your full resume
- Already knows the job description
- Remembers everything said in the conversation
- Rewrites your bullet points specifically for the target company
- Gives advice grounded in a RAG knowledge base of career expertise

### 3. Cover Letter Generator
Generates a personalised cover letter that:
- Opens with your strongest relevant achievement
- Addresses your gaps honestly and reframes them as strengths
- Sounds human — not templated
- Is specific to the company and role

### 4. Enhanced Resume Download
After the AI coach rewrites your bullets:
- App automatically extracts the improved bullets from chat
- Replaces original bullets in your resume structure
- Generates a clean, professionally formatted PDF
- Download your AI-optimised resume in one click

### 5. Live Job Listings
- Searches real live job openings matching your profile
- Uses Claude AI to extract the right search keywords from your resume
- Works for any profession — PM, engineer, designer, analyst
- Covers India, UK, and USA

### 6. Analysis Report PDF
Download a complete PDF containing:
- Your match score with colour-coded verdict
- Full skills analysis (green matched, red missing)
- Strengths and gaps
- Recommendation
- Cover letter (if generated)

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                       │
│              (app.py + login.py)                     │
│         Port 8501 — What the user sees               │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP requests
┌─────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                      │
│                    (api.py)                          │
│              Port 8000 — REST API                    │
│                                                      │
│  POST /analyze        POST /cover-letter             │
│  POST /chat           POST /jobs                     │
│  POST /auth/register  POST /auth/login               │
│  GET  /auth/google    GET  /health                   │
└──┬──────────┬──────────┬──────────┬─────────────────┘
   │          │          │          │
┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌──▼──────────┐
│PDF  │  │Resume │  │  JD   │  │  Career     │
│Read │  │Parser │  │Matcher│  │  Coach      │
│     │  │Chain  │  │Chain  │  │  Agent      │
└──┬──┘  └───┬───┘  └───┬───┘  └──┬──────────┘
   │          │          │          │
┌──▼──────────▼──────────▼──────────▼─────────────────┐
│                  Claude Sonnet API                    │
│              200k token context window               │
└─────────────────────────────────────────────────────┘
   │                              │
┌──▼──────────┐          ┌────────▼────────┐
│    FAISS    │          │   Adzuna API    │
│  Vector DB  │          │  Live Jobs      │
│ RAG Knowledge│          │  Search         │
└─────────────┘          └─────────────────┘
```

---

## 🧠 GenAI Concepts Implemented

| Concept | Where Used |
|---|---|
| Prompt Engineering | All chains — role prompting, output constraints |
| Chain of Thought | JD Matcher — step by step analysis |
| LangChain LCEL | Resume parser and JD matcher chains |
| RAG | Knowledge base with FAISS vector store |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Context Injection | Career coach system prompt |
| Conversation Memory | RunnableWithMessageHistory |
| Semantic Search | FAISS similarity search |
| Structured Output | JsonOutputParser for all chains |
| LangSmith | Full chain observability and tracing |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| LLM | Claude Sonnet (Anthropic) | 200k context window, best JSON extraction |
| Framework | LangChain | Chains, memory, agents, observability |
| Backend | FastAPI + Uvicorn | REST API, async, auto documentation |
| Frontend | Streamlit | Python-only, fast to build |
| Database | SQLite + SQLAlchemy | User accounts, zero config |
| Auth | JWT + Google OAuth | Secure, production-ready |
| Vector DB | FAISS | Local, free, fast similarity search |
| Embeddings | HuggingFace (MiniLM) | Free, runs locally, no API cost |
| PDF | pdfplumber + reportlab | Extract and generate PDFs |
| Jobs API | Adzuna | Free, covers India/UK/US |
| Observability | LangSmith | Chain tracing and debugging |

---

## 📁 Project Structure
```
resume-ai-coach/
├── api.py                    FastAPI backend — all endpoints
├── app.py                    Streamlit frontend
├── login.py                  Authentication UI
├── pipeline.py               Orchestration layer
│
├── chains/
│   ├── resume_parser.py      PDF text → structured JSON
│   ├── jd_matcher.py         Resume + JD → match analysis
│   ├── cover_letter.py       Analysis → cover letter
│   ├── bullet_extractor.py   Chat response → bullet points
│   └── resume_enhancer.py    Apply improvements to resume
│
├── tools/
│   ├── pdf_reader.py         PDF → clean text
│   ├── pdf_exporter.py       Data → formatted PDF
│   └── jobs_api.py           Profile → live job listings
│
├── agent/
│   └── career_coach.py       Conversational AI coach
│
├── vectorstore/
│   ├── knowledge_base.py     Expert career knowledge
│   └── embedder.py           Build and query FAISS index
│
├── auth/
│   ├── database.py           SQLite setup
│   ├── models.py             User model
│   ├── auth_handler.py       JWT tokens, password hashing
│   └── google_oauth.py       Google OAuth flow
│
└── docs/
    ├── DECISIONS.md          Every technical decision documented
    └── MVP_SUMMARY.md        Quick reference guide
```

---

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.11+
- Anthropic API key
- Adzuna API credentials
- Google OAuth credentials (for Google login)
- LangSmith API key (for observability)

### Installation
```bash
# Clone the repository
git clone https://github.com/bhardwajvaishali47-ux/resume-ai-coach
cd resume-ai-coach

# Create virtual environment
python -m venv venv_ai
source venv_ai/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_anthropic_key
ADZUNA_APP_ID=your_adzuna_id
ADZUNA_APP_KEY=your_adzuna_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=resume-ai-coach
LANGCHAIN_API_KEY=your_langsmith_key
SECRET_KEY=your_jwt_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501/
```

### Build the knowledge base
```bash
python vectorstore/embedder.py
```

### Run the application

Terminal 1 — FastAPI backend:
```bash
python api.py
```

Terminal 2 — Streamlit frontend:
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 🔑 Key Technical Decisions

**Why Claude Sonnet over GPT-4o?**
200k token context window vs 128k. The full resume, job description, chat history, and analysis results all fit in a single API call without memory compression.

**Why LangChain?**
Provides chains, memory, agents, and LangSmith observability out of the box. Building these from scratch would add weeks of work.

**Why FastAPI over Flask?**
Async support, automatic Swagger documentation, Pydantic validation, and significantly faster performance under concurrent load.

**Why FAISS over a cloud vector database?**
Zero cost, runs locally, no external dependency. For a demo and portfolio app, local FAISS is the right choice. Cloud migration (Pinecone, Weaviate) is straightforward when needed.

**Why SQLite over PostgreSQL?**
Zero configuration for development. SQLAlchemy ORM means the database can be swapped to PostgreSQL for production with one line change.

---

## 📊 LangSmith Observability

Every chain run is traced in LangSmith. You can see:
- Exact prompts sent to Claude
- Exact responses received
- Token count per API call
- Latency per step
- Full agent reasoning chain

---

## 🗺️ Roadmap

### V3 — Production Ready
- [ ] Redis session store for persistent sessions
- [ ] Deploy to Railway with both servers
- [ ] Email verification on registration
- [ ] Rate limiting per user

### V4 — Enhanced Features  
- [ ] Job application automation
- [ ] Interview preparation module
- [ ] Resume version history
- [ ] Multi-language support

---

## 👤 About

Built by **Vaishali Bhardwaj** — AI Product Manager

This project was built to solve a real personal problem — the lack of genuinely useful, personalised career guidance for professionals transitioning into AI roles. Every technical decision was deliberate and documented in `docs/DECISIONS.md`.

- LinkedIn: [linkedin.com/in/vaishalibhardwaj](https://linkedin.com/in/vaishalibhardwaj)
- GitHub: [github.com/bhardwajvaishali47-ux](https://github.com/bhardwajvaishali47-ux)

---

*Powered by Claude AI · LangChain · FastAPI · Streamlit*