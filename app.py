import streamlit as st
import os
import uuid
import requests
from dotenv import load_dotenv
from login import show_login_page
from tools.pdf_exporter import create_resume_pdf, create_analysis_report
from chains.resume_enhancer import enhance_resume_with_chat, get_enhancement_summary

load_dotenv()

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="AI Resume Coach",
    page_icon="📄",
    layout="wide"
)

if not st.session_state.get("authenticated"):
    show_login_page()
    st.stop()


def call_analyze_api(pdf_file, job_description: str) -> dict:
    """
    Calls FastAPI /analyze endpoint.
    Sends PDF file and job description.
    Returns complete analysis result.
    """
    files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
    data = {"job_description": job_description}
    response = requests.post(f"{API_BASE_URL}/analyze", files=files, data=data)
    response.raise_for_status()
    return response.json()


def call_cover_letter_api(
    parsed_resume: dict,
    job_description: str,
    match_result: dict
) -> str:
    """
    Calls FastAPI /cover-letter endpoint.
    Returns generated cover letter as string.
    """
    payload = {
        "parsed_resume": parsed_resume,
        "job_description": job_description,
        "match_result": match_result
    }
    response = requests.post(f"{API_BASE_URL}/cover-letter", json=payload)
    response.raise_for_status()
    return response.json()["cover_letter"]


def call_chat_api(
    message: str,
    session_id: str,
    parsed_resume: dict,
    job_description: str,
    match_result: dict
) -> str:
    """
    Calls FastAPI /chat endpoint.
    Sends message and session ID.
    Returns agent response as string.
    """
    payload = {
        "message": message,
        "session_id": session_id,
        "parsed_resume": parsed_resume,
        "job_description": job_description,
        "match_result": match_result
    }
    response = requests.post(f"{API_BASE_URL}/chat", json=payload)
    response.raise_for_status()
    return response.json()["response"]


def call_jobs_api(
    parsed_resume: dict,
    match_result: dict,
    job_description: str,
    country: str
) -> dict:
    """
    Calls FastAPI /jobs endpoint.
    Returns live job listings matching the profile.
    """
    payload = {
        "parsed_resume": parsed_resume,
        "match_result": match_result,
        "job_description": job_description,
        "country": country
    }
    response = requests.post(f"{API_BASE_URL}/jobs", json=payload)
    response.raise_for_status()
    return response.json()


col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("AI Resume Coach")
with col_logout:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
user_name = st.session_state.get("user_name", "")
user_email = st.session_state.get("user_email", "")
if user_name:
    st.text(f"👋 Welcome back {user_name} | {user_email}")
st.markdown("Upload your resume and paste a job description to get an instant match analysis powered by Claude AI.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Your Resume")
    upload_file = st.file_uploader(
        "Choose your resume PDF",
        type=["pdf"],
        help="Upload a text-based PDF exported from Word or Google Docs"
    )

with col2:
    st.subheader("Paste Your Job Description")
    job_description = st.text_area(
        "Paste the full job description here",
        height=300,
        placeholder="Copy and paste the job description from LinkedIn, Naukri, or any job portal..."
    )

st.divider()

analyse_button = st.button(
    "Analyse my Resume",
    type="primary",
    use_container_width=True
)

if analyse_button and not st.session_state.get("analysis_done"):
    if upload_file is None:
        st.warning("Please upload your resume PDF first.")
    elif not job_description.strip():
        st.warning("Please paste a job description first.")
    else:
        with st.spinner("Analysing your resume with Claude AI... This may take 20-30 seconds."):
            result = call_analyze_api(upload_file, job_description)

        if "error" in result:
            st.error(result["error"])
        else:
            st.session_state["result"] = result
            st.session_state["analysis_done"] = True
            st.session_state["job_description"] = job_description
            st.session_state["session_id"] = str(uuid.uuid4())


# RESULTS SECTION
if st.session_state.get("analysis_done"):
    result = st.session_state["result"]
    parsed = result["parsed_resume"]
    match = result["match_result"]

    st.divider()
    st.header("Your Analysis Result")

    score = match.get("match_score", 0)
    st.subheader(f"Match Score: {score}%")
    st.progress(score / 100)

    if score >= 75:
        st.success("Strong match. You should apply for this role.")
    elif score >= 50:
        st.warning("Moderate match. Consider addressing the gaps before applying.")
    else:
        st.error("Low match. Significant gaps need to be addressed.")

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Matched Skills")
        for skill in match.get("matched_skills", []):
            st.markdown(f"✅ {skill}")

    with col4:
        st.subheader("Missing Skills")
        for skill in match.get("missing_skills", []):
            st.markdown(f"❌ {skill}")

    st.divider()

    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Your Strengths")
        for strength in match.get("strengths", []):
            st.markdown(f"⭐ {strength}")

    with col6:
        st.subheader("Areas to Improve")
        for gap in match.get("gaps", []):
            st.markdown(f"⚠️ {gap}")

    st.divider()

    st.subheader("Recommendation")
    st.info(match.get("recommendation", ""))

    st.divider()

    st.subheader("Cover Letter Generator")
    st.markdown("Generate a personalised cover letter tailored to this specific role.")

    if st.button("Generate Cover Letter", type="secondary"):
        with st.spinner("Writing your cover letter..."):
            cover_letter = call_cover_letter_api(
                result["parsed_resume"],
                st.session_state["job_description"],
                result["match_result"]
            )
            st.session_state["cover_letter"] = cover_letter

    if st.session_state.get("cover_letter"):
        st.text_area(
            "Your Cover Letter",
            value=st.session_state["cover_letter"],
            height=400
        )
        st.caption("Copy the text above and paste it into your application.")

    st.divider()

    st.subheader("Your Parsed Resume")
    with st.expander("Click to view full parsed resume data"):
        st.json(parsed)

    st.divider()

    st.subheader("Download Your Analysis Report")
    st.markdown("Download a complete PDF report with your match score, skills analysis, recommendation, and cover letter.")

    if st.button("Download Analysis Report", type="secondary"):
        with st.spinner("Generating your report..."):
            cover_letter_text = st.session_state.get("cover_letter", "")
            report_path = "analysis_report.pdf"
            create_analysis_report(
                result["parsed_resume"],
                st.session_state["job_description"],
                result["match_result"],
                cover_letter_text,
                report_path
            )
            with open(report_path, "rb") as f:
                report_bytes = f.read()

            name = result["parsed_resume"].get("name", "Candidate")
            clean_name = name.replace(" ", "_")
            file_name = f"{clean_name}_Analysis_Report.pdf"

            st.session_state["report_bytes"] = report_bytes
            st.session_state["report_file_name"] = file_name

    if st.session_state.get("report_bytes"):
        st.download_button(
            label="Click here to download your report",
            data=st.session_state["report_bytes"],
            file_name=st.session_state["report_file_name"],
            mime="application/pdf"
        )


# LIVE JOBS SECTION
if st.session_state.get("analysis_done"):
    st.divider()
    st.header("Live Job Listings For You")
    st.markdown("Real job openings matched to your profile from across India.")

    col_country1, col_country2 = st.columns([3, 1])

    with col_country2:
        country = st.selectbox(
            "Country",
            options=["in", "gb", "us"],
            format_func=lambda x: {"in": "India", "gb": "UK", "us": "USA"}[x]
        )

    if st.button("Find Matching Jobs", type="secondary"):
        with st.spinner("Searching live job listings..."):
            result = st.session_state["result"]
            jobs_data = call_jobs_api(
                result["parsed_resume"],
                result["match_result"],
                st.session_state.get("job_description", ""),
                country
            )
            st.session_state["jobs_data"] = jobs_data

    if st.session_state.get("jobs_data"):
        jobs_data = st.session_state["jobs_data"]
        jobs = jobs_data["jobs"]
        keywords = jobs_data["keywords_used"]

        st.caption(
            f"Searched for: '{keywords}' — Found {jobs_data['jobs_found']} listings"
        )

        if jobs:
            for i, job in enumerate(jobs, 1):
                with st.expander(
                    f"{job['title']} — {job['company']} | {job['location']}"
                ):
                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.markdown(f"**Company:** {job['company']}")
                        st.markdown(f"**Location:** {job['location']}")
                        st.markdown(f"**Salary:** {job['salary']}")
                        st.markdown(f"**Posted:** {job['created']}")

                    with col_b:
                        st.markdown("**Description:**")
                        st.markdown(job['description'])

                    st.markdown(f"[Apply Now →]({job['apply_url']})")
        else:
            st.warning(
                "No jobs found for your profile. Try a different country or run the analysis again."
            )


# CHAT SECTION
if st.session_state.get("analysis_done"):
    st.divider()
    st.header("Chat with your AI Career Coach")
    st.markdown("Ask anything about your resume, request rewrites, or get specific advice.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask your career coach anything...")

    if user_input:
        st.session_state["messages"].append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state["result"]
                response = call_chat_api(
                    user_input,
                    st.session_state.get("session_id", "default"),
                    result["parsed_resume"],
                    st.session_state["job_description"],
                    result["match_result"]
                )
            st.markdown(response)

        st.session_state["messages"].append({
            "role": "assistant",
            "content": response
        })


# ENHANCED RESUME DOWNLOAD SECTION
if st.session_state.get("analysis_done"):
    st.divider()
    st.subheader("Download Enhanced Resume")
    st.markdown(
        "After chatting with your AI coach to improve your bullets, "
        "download your enhanced resume as a PDF."
    )

    messages = st.session_state.get("messages", [])
    assistant_count = sum(1 for m in messages if m["role"] == "assistant")

    if assistant_count > 0:
        st.info(
            f"Found {assistant_count} coaching responses in your chat. "
            "Click below to apply improvements to your resume."
        )

        if st.button("Generate Enhanced Resume", type="secondary"):
            with st.spinner("Applying improvements from your coaching session..."):
                result = st.session_state["result"]
                enhanced_resume = enhance_resume_with_chat(
                    result["parsed_resume"],
                    st.session_state["messages"]
                )

                summary = get_enhancement_summary(
                    result["parsed_resume"],
                    enhanced_resume
                )

                enhanced_path = "enhanced_resume.pdf"
                create_resume_pdf(enhanced_resume, enhanced_path)

                with open(enhanced_path, "rb") as f:
                    enhanced_bytes = f.read()

                name = result["parsed_resume"].get("name", "Candidate")
                clean_name = name.replace(" ", "_")
                enhanced_file_name = f"{clean_name}_Enhanced_Resume.pdf"

                st.session_state["enhanced_bytes"] = enhanced_bytes
                st.session_state["enhanced_file_name"] = enhanced_file_name
                st.session_state["enhancement_summary"] = summary

        if st.session_state.get("enhanced_bytes"):
            st.success(st.session_state["enhancement_summary"])
            st.download_button(
                label="Download Enhanced Resume PDF",
                data=st.session_state["enhanced_bytes"],
                file_name=st.session_state["enhanced_file_name"],
                mime="application/pdf"
            )
    else:
        st.info(
            "Chat with your AI coach first to get bullet point improvements, "
            "then come back here to download your enhanced resume."
        )