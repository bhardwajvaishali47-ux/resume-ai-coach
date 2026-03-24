import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def create_resume_pdf(parsed_resume: dict, output_path: str) -> str:
    """
    Creates a professionally formatted PDF resume
    from the parsed resume dictionary.

    Input:
        parsed_resume: dictionary from resume_parser chain
        output_path: where to save the PDF file

    Output:
        path to the created PDF file
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()
    # ParagraphStyle — creating custom text styles
    name_style = ParagraphStyle(
        "NameStyle",
        parent=styles["Normal"],#inherits base settings from the Normal style, then overrides specific properties.
        fontSize=20,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),#a dark navy colour for headings.
        alignment=TA_CENTER, #text alignment
        spaceAfter=4 # 4 points of space below this paragraph before the next element.
    )

    contact_style = ParagraphStyle(
        "ContactStyle",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica",
        textColor=colors.HexColor("#444444"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=12,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=colors.HexColor("#222222"),
        spaceAfter=3,
        leading=14
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=styles["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=colors.HexColor("#222222"),
        leftIndent=12,
        spaceAfter=2,
        leading=14
    )

    bold_style = ParagraphStyle(
        "BoldStyle",
        parent=styles["Normal"],
        fontSize=9.5,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#222222"),
        spaceAfter=1
    )

    
    #reportlab builds PDFs using a concept called flowables — elements that flow down the page one after another. You create a list called story and append elements to it. When you call doc.build(story), reportlab places each element on the page in order.
    
    
    story = []

    name = parsed_resume.get("name", "")
    email = parsed_resume.get("email", "")
    phone = parsed_resume.get("phone", "")

    story.append(Paragraph(name, name_style)) #Paragraph(text, style)
#A block of text with a specific style applied. The style controls font, size, colour, alignment, spacing.

    contact_parts = []
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    contact_line = " | ".join(contact_parts)
    story.append(Paragraph(contact_line, contact_style))

    story.append(HRFlowable(
        width="100%",
        thickness=1.5,
        color=colors.HexColor("#1a1a2e")
    ))
    story.append(Spacer(1, 10))
    summary = parsed_resume.get("summary", "")
    if summary:
        story.append(Paragraph("PROFESSIONAL SUMMARY", section_header_style))
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#cccccc")
        ))
        story.append(Spacer(1, 8)) #Spacer(width, height)An invisible gap. Spacer(1, 4) adds 4 points of vertical space. Used to create breathing room between sections.
        story.append(Paragraph(summary, body_style))

    skills = parsed_resume.get("skills", [])
    if skills:
        story.append(Paragraph("CORE COMPETENCIES", section_header_style))
        #HRFlowable(...)A horizontal line across the page. Used as section dividers.
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#cccccc")
        ))
        story.append(Spacer(1, 4))
        skills_text = " • ".join(skills)
        story.append(Paragraph(skills_text, body_style))

    experience = parsed_resume.get("experience", [])
    if experience:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_header_style))
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#cccccc")
        ))
        story.append(Spacer(1, 4))

        for job in experience:
            role = job.get("role", "")
            company = job.get("company", "")
            duration = job.get("duration", "")

            story.append(Paragraph(role, bold_style))

            company_line = f"{company} | {duration}"
            story.append(Paragraph(company_line, body_style))

            bullets = job.get("bullets", [])
            for bullet in bullets:
                story.append(Paragraph(f"• {bullet}", bullet_style))

            story.append(Spacer(1, 6))

    education = parsed_resume.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", section_header_style))
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#cccccc")
        ))
        story.append(Spacer(1, 4))

        for edu in education:
            degree = edu.get("degree", "")
            institution = edu.get("institution", "")
            year = edu.get("year", "")

            edu_line = f"{degree} — {institution} {year}"
            story.append(Paragraph(edu_line, body_style))

    certifications = parsed_resume.get("certifications", [])
    if certifications:
        story.append(Paragraph("CERTIFICATIONS", section_header_style))
        story.append(HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor("#cccccc")
        ))
        story.append(Spacer(1, 4))

        for cert in certifications:
            story.append(Paragraph(f"• {cert}", bullet_style))

    doc.build(story)
    return output_path

def create_analysis_report(
    parsed_resume: dict,
    job_description: str,
    match_result: dict,
    cover_letter: str,
    output_path: str
) -> str:
    """
    Creates a professionally formatted analysis report PDF.
    Contains match score, skills analysis, strengths,
    gaps, recommendation, and cover letter.

    This is something the user cannot get elsewhere —
    a complete job application intelligence report.
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Normal"],
        fontSize=18,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#444444"),
        alignment=TA_CENTER,
        spaceAfter=16
    )

    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=18,
        spaceAfter=4
    )

    score_style = ParagraphStyle(
        "ScoreStyle",
        parent=styles["Normal"],
        fontSize=28,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
        spaceAfter=4
    )

    score_label_style = ParagraphStyle(
        "ScoreLabelStyle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#222222"),
        spaceAfter=4,
        leading=15
    )

    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#222222"),
        leftIndent=12,
        spaceAfter=3,
        leading=15
    )

    green_bullet_style = ParagraphStyle(
        "GreenBullet",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#1a7a1a"),
        leftIndent=12,
        spaceAfter=3,
        leading=15
    )

    red_bullet_style = ParagraphStyle(
        "RedBullet",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#cc0000"),
        leftIndent=12,
        spaceAfter=3,
        leading=15
    )

    story = []

    name = parsed_resume.get("name", "Candidate")
    match_score = match_result.get("match_score", 0)
    matched_skills = match_result.get("matched_skills", [])
    missing_skills = match_result.get("missing_skills", [])
    strengths = match_result.get("strengths", [])
    gaps = match_result.get("gaps", [])
    recommendation = match_result.get("recommendation", "")

    story.append(Paragraph("AI Resume Analysis Report", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Prepared for: {name}", subtitle_style))

    jd_first_line = job_description.split('\n')[0][:80]
    story.append(Paragraph(f"Role: {jd_first_line}", subtitle_style))

    story.append(HRFlowable(
        width="100%",
        thickness=2,
        color=colors.HexColor("#1a1a2e")
    ))

    story.append(Spacer(1, 16))
    story.append(Paragraph(f"{match_score}%", score_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Match Score", score_label_style))
    story.append(Spacer(1, 8))

    if match_score >= 75:
        verdict = "Strong Match — You should apply for this role"
        verdict_color = colors.HexColor("#1a7a1a")
    elif match_score >= 50:
        verdict = "Moderate Match — Address the gaps before applying"
        verdict_color = colors.HexColor("#cc8800")
    else:
        verdict = "Low Match — Significant gaps need to be addressed"
        verdict_color = colors.HexColor("#cc0000")

    verdict_style = ParagraphStyle(
        "VerdictStyle",
        parent=styles["Normal"],
        fontSize=11,
        fontName="Helvetica-Bold",
        textColor=verdict_color,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    story.append(Paragraph(verdict, verdict_style))

    story.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=colors.HexColor("#cccccc")
    ))

    story.append(Paragraph("Matched Skills", section_header_style))
    for skill in matched_skills:
        story.append(Paragraph(f"✓  {skill}", green_bullet_style))

    story.append(Paragraph("Missing Skills", section_header_style))
    for skill in missing_skills:
        story.append(Paragraph(f"✗  {skill}", red_bullet_style))

    story.append(Paragraph("Your Strengths for This Role",
                            section_header_style))
    for i, strength in enumerate(strengths, 1):
        story.append(Paragraph(f"{i}.  {strength}", bullet_style))

    story.append(Paragraph("Areas to Address", section_header_style))
    for i, gap in enumerate(gaps, 1):
        story.append(Paragraph(f"{i}.  {gap}", bullet_style))

    story.append(Paragraph("Recommendation", section_header_style))
    story.append(HRFlowable(
        width="100%",
        thickness=0.5,
        color=colors.HexColor("#cccccc")
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(recommendation, body_style))

    if cover_letter:
        story.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor("#1a1a2e")
        ))
        story.append(Paragraph("Cover Letter", title_style))
        story.append(Spacer(1, 8))

        for para in cover_letter.split('\n'):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 4))

    doc.build(story)
    return output_path


if __name__ == "__main__":
    test_resume = {
        "name": "Vaishali Bhardwaj",
        "email": "bhardwajvaishali47@gmail.com",
        "phone": "+91-8860696512",
        "summary": "Product Manager with 9+ years of experience leading AI/ML-enabled and data-centric SaaS platforms. Google Cloud Certified Generative AI Leader with hands-on LLM product experience.",
        "skills": [
            "Product Roadmap Strategy",
            "AI/ML Product Integration",
            "LLM Applications",
            "PRD Authoring",
            "Agile Delivery",
            "KPI Definition",
            "GCP and BigQuery",
            "Stakeholder Management"
        ],
        "experience": [
            {
                "company": "BT Group (Openreach)",
                "role": "Product Owner / Product Manager — AI & Enterprise Data",
                "duration": "Dec 2021 – Jan 2026",
                "bullets": [
                    "Defined product vision and multi-year roadmap for AI-enabled analytics platforms supporting 10M+ broadband customers",
                    "Integrated Generative AI (Vertex AI) to automate KPI insights, reducing manual analysis effort by 25%",
                    "Delivered 40% improvement in data processing efficiency through GCP migration and pipeline optimisation"
                ]
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Computer Applications",
                "institution": "Delhi University",
                "year": "2015"
            }
        ],
        "certifications": [
            "Google Cloud Certified Generative AI Leader",
            "SAFe 6.0 Certified Product Owner / Product Manager (POPM)"
        ]
    }

    output = create_resume_pdf(test_resume, "test_output_resume.pdf")
    print(f"PDF created: {output}")
    
    #SimpleDocTemplateThe document itself. Sets page size, margins, and output file path. 
    
