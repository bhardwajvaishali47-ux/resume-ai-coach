# 🎯 AI Resume Coach — React Frontend

> An AI-powered career coaching platform that analyses your resume against any job description, provides personalised match insights, and coaches you through improving your application — now with a production-grade React frontend built on the **Snitch design system**.

---

## 🆕 What Changed in This Version

This version represents a full frontend migration from **Streamlit → React + TypeScript**, while keeping the FastAPI backend 100% intact.

| Layer | Before (V1) | After (V2) |
|---|---|---|
| Frontend UI | Streamlit (Python) | React + Vite + TypeScript |
| Design System | None — ad hoc styles | Snitch design system |
| Prototyping Tool | bolt.new | Removed — full ownership |
| Login Page | bolt.new prototype | Snitch-matched React component |
| Dashboard | Streamlit multipage | Single-page React dashboard |
| Auth | Streamlit session state | JWT via React AuthContext |
| Routing | Streamlit pages | React Router v6 |
| Fonts | Default Streamlit | Inter + JetBrains Mono |
| Theming | None | CSS custom properties + Tailwind |

**Why migrate?**
- Streamlit is excellent for data prototyping but not for production-quality user interfaces
- bolt.new creates a proprietary lock-in — code cannot be version-controlled or extended cleanly
- The Snitch design system required a proper component-based architecture to implement correctly
- A React frontend enables future features: real-time updates, animations, offline support, PWA

---

## ✨ What This App Does

### The Problem
Job seekers spend hours tailoring resumes with no clear guidance on what actually matters for a specific role. Generic ATS tools give keyword scores but no real advice. There is no tool that tells you *exactly* how to position yourself for the role you want.

### The Solution

Upload your resume PDF + paste any job description. Get back:

| Feature | Description |
|---|---|
| **Match Score** | 0–100% score with colour-coded verdict (Strong / Good / Moderate / Low) |
| **Skills Delta** | ✅ Matched · ⚠ Partial · ❌ Missing — all as visual pill badges |
| **Competency Radar** | SVG polygon radar chart comparing your profile to the role |
| **AI Career Coach** | Conversational chat that knows your full resume and the JD |
| **Bullet Rewriter** | Coach rewrites your experience bullets specifically for the target role |
| **Enhanced Resume PDF** | Download your improved resume as a formatted PDF in one click |
| **Cover Letter** | Personalised cover letter that addresses gaps honestly |
| **Live Job Listings** | Real openings from Adzuna API — India, UK, USA |
| **Analysis Report** | Full breakdown: strengths, gaps, recommendation |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              React Frontend (NEW — V2)                   │
│         React + Vite + TypeScript + Tailwind             │
│              Port 5173 — Snitch Design System            │
│                                                          │
│  LoginPage.tsx          DashboardPage.tsx                │
│  (Auth + Google OAuth)  (All features — single file)     │
└─────────────────┬───────────────────────────────────────┘
                  │ HTTP + JWT Bearer token
┌─────────────────▼───────────────────────────────────────┐
│                  FastAPI Backend (UNCHANGED)              │
│                    (api.py) — Port 8000                  │
│                                                          │
│  POST /analyze          POST /cover-letter               │
│  POST /chat             POST /jobs                       │
│  POST /enhance-resume   ← NEW endpoint added in V2       │
│  POST /auth/register    POST /auth/login                 │
│  GET  /auth/google/url  GET  /health                     │
└──┬──────────┬──────────┬──────────┬─────────────────────┘
   │          │          │          │
┌──▼──┐  ┌───▼───┐  ┌───▼───┐  ┌──▼──────────┐
│PDF  │  │Resume │  │  JD   │  │  Career     │
│Read │  │Parser │  │Matcher│  │  Coach      │
│     │  │Chain  │  │Chain  │  │  Agent      │
└──┬──┘  └───┬───┘  └───┬───┘  └──┬──────────┘
   │          │          │          │
┌──▼──────────▼──────────▼──────────▼─────────────────────┐
│                  Claude Sonnet API                        │
│              200k token context window                   │
└─────────────────────────────────────────────────────────┘
   │                              │
┌──▼──────────┐          ┌────────▼────────┐
│    FAISS    │          │   Adzuna API    │
│  Vector DB  │          │  Live Jobs      │
│ RAG Knowledge│          │  Search         │
└─────────────┘          └─────────────────┘
```

---

## 🛠️ Tech Stack

### Backend (unchanged from V1)

| Layer | Technology | Why |
|---|---|---|
| LLM | Claude Sonnet (Anthropic) | 200k context window, best JSON extraction |
| Framework | LangChain | Chains, memory, agents, observability |
| Backend | FastAPI + Uvicorn | REST API, async, Pydantic validation |
| Database | SQLite + SQLAlchemy | User accounts, zero config |
| Auth | JWT + Google OAuth | Secure, production-ready |
| Vector DB | FAISS | Local, free, fast similarity search |
| Embeddings | HuggingFace MiniLM | Free, runs locally |
| PDF | pdfplumber + reportlab | Extract and generate PDFs |
| Jobs API | Adzuna | Free, covers India/UK/US |
| Observability | LangSmith | Chain tracing and debugging |

### Frontend (new in V2)

| Layer | Technology | Why |
|---|---|---|
| Framework | React 18 + Vite | Fast HMR, production-grade builds |
| Language | TypeScript | Type safety across all API contracts |
| Styling | Tailwind CSS + inline styles | Snitch design token compatibility |
| Design System | Snitch | Consistent dark-theme visual language |
| Fonts | Inter + JetBrains Mono | Inter = body, Mono = labels/metrics |
| Routing | React Router v6 | Client-side navigation |
| Auth State | React Context (AuthContext) | JWT token + user name/email globally |
| Charts | Pure SVG | No external chart library — score ring + radar chart |
| PDF Download | Browser Blob API | Base64 → Uint8Array → Blob → download |

---

## 📁 Project Structure

### Backend — `resume-ai-coach/`
```
resume-ai-coach/
├── api.py                    FastAPI backend — all endpoints
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
│   ├── pdf_exporter.py       Data → formatted PDF (ReportLab)
│   └── jobs_api.py           Profile → live job listings
│
├── agent/
│   └── career_coach.py       Conversational AI coach (LangChain)
│
├── vectorstore/
│   ├── knowledge_base.py     Expert career knowledge
│   └── embedder.py           Build and query FAISS index
│
└── auth/
    ├── database.py           SQLite setup
    ├── models.py             User model
    ├── auth_handler.py       JWT tokens, password hashing
    └── google_oauth.py       Google OAuth flow
```

### Frontend — `resume-frontend/`
```
resume-frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.tsx     Login + Create Account (Snitch design)
│   │   └── DashboardPage.tsx Full dashboard — all features in one component
│   │
│   ├── components/
│   │   └── Login.tsx         Login form component
│   │
│   ├── context/
│   │   └── AuthContext.tsx   JWT token + user state (global)
│   │
│   └── App.tsx               Routing: / → Login, /dashboard → Dashboard
│
├── tailwind.config.js        Extended with all Snitch colour tokens
├── vite.config.ts
└── tsconfig.json
```

---

## 🧠 GenAI Concepts Implemented

| Concept | Where Used |
|---|---|
| Prompt Engineering | All chains — role prompting, output constraints |
| Chain of Thought | JD Matcher — step-by-step analysis |
| LangChain LCEL | Resume parser and JD matcher chains |
| RAG | Knowledge base with FAISS vector store |
| Embeddings | HuggingFace all-MiniLM-L6-v2 |
| Context Injection | Career coach system prompt with full resume + JD |
| Conversation Memory | RunnableWithMessageHistory — coach remembers chat |
| Semantic Search | FAISS similarity search for career knowledge |
| Structured Output | JsonOutputParser for all chains |
| Bullet Extraction | Claude extracts rewritten bullets from chat responses |
| Resume Enhancement | Merges improved bullets back into resume structure |
| LangSmith | Full chain observability and tracing |

---

## 🎨 Snitch Design System — Token Reference

The React frontend implements the Snitch design system throughout. All colours are used as CSS values in inline styles and Tailwind config extensions.

| Token | Value | Usage |
|---|---|---|
| `surface` | `#101319` | Page background, nav bar |
| `surface-container` | `#191C22` | Cards, sidebar |
| `surface-container-high` | `#272A31` | Active states, chat bubbles |
| `primary` (coral) | `#FFB3AE / #FF5351` | CTAs, active nav, logo |
| `secondary` (teal) | `#43E1BA` | Matched skills, success |
| `tertiary` (amber) | `#FFB347` | Partial matches, warnings |
| `error` (red) | `#FFB4AB` | Missing skills, low scores |
| `on-surface` | `#E1E2EB` | Primary text |
| `on-surface-variant` | `#AB8886` | Secondary text, labels |
| `outline-variant` | `rgba(91,64,62,0.13)` | Card borders |
| Font — Body | Inter | All body text |
| Font — Labels | JetBrains Mono | Metrics, badges, nav labels |

---

## 🔑 Key Technical Decisions (V2 Frontend)

**Why React over continuing with Streamlit?**
Streamlit re-renders the entire page on every interaction. A career coaching tool needs smooth, stateful UX — collapsible sidebar, live chat, animated score rings, tab switching — none of which Streamlit handles gracefully.

**Why a single `DashboardPage.tsx` file?**
All dashboard features share the same state: `rawApiResponse` (the full `/analyze` result) must be accessible by chat, cover letter, jobs, and enhance-resume. Keeping everything in one component avoids prop-drilling or a global store. When the app grows, individual tab components can be extracted.

**Why `rawApiResponse` stored in state?**
The FastAPI `/chat`, `/cover-letter`, `/jobs`, and `/enhance-resume` endpoints all require `parsed_resume` + `job_description` + `match_result` in every request body. These come from the initial `/analyze` response. Storing the full raw response in state means every subsequent call can send the required context without re-fetching.

**Why no external chart library for the radar/score ring?**
Zero dependencies, zero bundle size cost, and full control over the Snitch colour tokens. The SVG radar chart and animated score ring are ~40 lines of pure SVG each.

**Why PDF download via base64?**
The `/enhance-resume` endpoint generates the PDF server-side using ReportLab and returns it as a base64 string. The frontend decodes it with `atob()`, creates a `Blob`, and triggers a programmatic download — no file system access required on either side.

**Why AuthContext stores `userName` and `userEmail` separately?**
The Snitch nav bar needs the user's name immediately on render — before any API call. Storing `user_name` and `user_email` as flat localStorage keys (not a JSON object) means they survive page refresh and are accessible synchronously.

---

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key
- Adzuna API credentials
- Google OAuth credentials
- LangSmith API key

### Backend Setup

```bash
# Clone the backend
git clone https://github.com/bhardwajvaishali47-ux/resume-ai-coach
cd resume-ai-coach

# Create and activate virtual environment
python -m venv venv_ai
source venv_ai/bin/activate

# Install dependencies
pip install -r requirements.txt

# Build the FAISS knowledge base (one-time)
python vectorstore/embedder.py
```

Create a `.env` file:
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
GOOGLE_REDIRECT_URI=http://localhost:5173/
```

### Frontend Setup

```bash
# Clone the frontend
git clone https://github.com/bhardwajvaishali47-ux/resume-frontend
cd resume-frontend

# Install dependencies
npm install
```

### Running the Application

**Terminal 1 — Backend:**
```bash
cd resume-ai-coach
source venv_ai/bin/activate
python api.py
# Runs on http://localhost:8000
```

**Terminal 2 — Frontend:**
```bash
cd resume-frontend
npm run dev
# Runs on http://localhost:5173
```

Open **`http://localhost:5173`** in your browser.

---

## 🚀 Complete User Flow

```
1. User visits localhost:5173
       ↓
2. Login Page — email/password or Google OAuth
       ↓
3. Token stored in localStorage via AuthContext
       ↓
4. Dashboard — Phase 1: Upload Panel
   • Upload resume PDF
   • Paste job description
   • Click "Analyse My Resume"
       ↓
5. POST /analyze → { parsed_resume, match_result }
   • Full response stored as rawApiResponse in state
       ↓
6. Dashboard — Phase 2: Full Dashboard
   • Match score ring animates in
   • Skills delta populates (matched / partial / missing)
   • Competency radar renders
   • AI coach sends welcome message
       ↓
7. User chats with AI Coach
   • POST /chat with full resume + JD context on every message
   • Coach rewrites bullets in conversation
       ↓
8. User goes to Enhanced Resume tab
   • Clicks "Apply Rewrites & Generate PDF"
   • POST /enhance-resume → bullet_extractor scans chat
   • resume_enhancer merges bullets → PDF generated
   • Base64 PDF returned → browser download triggered
       ↓
9. User generates Cover Letter
   • POST /cover-letter with full context
   • Displayed in scrollable panel with copy button
       ↓
10. User searches Job Listings
    • Selects country → POST /jobs
    • Live Adzuna results displayed as cards
```

---

## 📊 API Contract Reference

All endpoints require `Authorization: Bearer <token>` header.

| Endpoint | Method | Request Body | Response |
|---|---|---|---|
| `/analyze` | POST | `multipart: file, job_description` | `{ parsed_resume, match_result }` |
| `/chat` | POST | `{ message, session_id, parsed_resume, job_description, match_result }` | `{ response }` |
| `/cover-letter` | POST | `{ parsed_resume, job_description, match_result }` | `{ cover_letter }` |
| `/jobs` | POST | `{ country, parsed_resume, job_description, match_result }` | `{ jobs[] }` |
| `/enhance-resume` | POST | `{ parsed_resume, chat_messages[] }` | `{ enhanced_resume, summary, pdf_base64 }` |
| `/auth/register` | POST | `{ email, password, full_name }` | `{ token }` |
| `/auth/login` | POST | `{ email, password }` | `{ token, user }` |
| `/auth/google/url` | GET | — | `{ url }` |

---

## 🗺️ Roadmap

### V3 — Production Deployment
- [ ] Deploy React frontend to Vercel
- [ ] Deploy FastAPI to Railway
- [ ] Replace SQLite with PostgreSQL
- [ ] Replace FAISS with Pinecone (cloud vector search)
- [ ] Redis for session persistence
- [ ] Rate limiting per user
- [ ] Email verification on registration

### V4 — Enhanced Features
- [ ] Analysis history — save and compare past analyses
- [ ] Resume version history — track improvements over time
- [ ] Job alerts — email notifications for new matching roles
- [ ] Interview preparation module
- [ ] Multi-language resume support
- [ ] Analysis Report PDF download from dashboard

---

## 🐛 Known Issues

| Issue | Status | Workaround |
|---|---|---|
| Match score cached across sessions | Open | Click `+ New Analysis` to reset session |
| Enhanced Resume tab requires chat first | By design | Chat with coach to rewrite bullets, then download |
| Google OAuth redirect URI must match exactly | Config | Set `GOOGLE_REDIRECT_URI=http://localhost:5173/` |

---

## 👤 About

Built by **Vaishali Bhardwaj** — AI Product Manager

This project was built to solve a real personal problem — the lack of genuinely useful, personalised career guidance for professionals transitioning into AI roles. The V2 React frontend was built to demonstrate that AI product managers can own the full stack — from LangChain chains to TypeScript components.

- LinkedIn: [linkedin.com/in/vaishalibhardwaj](https://linkedin.com/in/vaishalibhardwaj)
- GitHub: [github.com/bhardwajvaishali47-ux](https://github.com/bhardwajvaishali47-ux)

---

## 📦 Both Repositories

| Repo | Description | Link |
|---|---|---|
| `resume-ai-coach` | FastAPI backend + all AI chains | [github.com/bhardwajvaishali47-ux/resume-ai-coach](https://github.com/bhardwajvaishali47-ux/resume-ai-coach) |
| `resume-frontend` | React + TypeScript frontend | [github.com/bhardwajvaishali47-ux/resume-frontend](https://github.com/bhardwajvaishali47-ux/resume-frontend) |

---

*Powered by Claude AI · LangChain · FastAPI · React · Snitch Design System*
