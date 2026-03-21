import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api/jobs"


def search_jobs(
    keywords: str,
    country: str = "in",
    results_per_page: int = 5,
    location: str = "india"
) -> list:
    """
    Searches Adzuna for live job listings.

    Input:
        keywords: search terms e.g. "AI Product Manager"
        country: country code — "in" for India, "gb" for UK
        results_per_page: how many jobs to return
        location: city or country to search in

    Output:
        list of job dictionaries with title, company,
        location, salary, description, apply link
    """

    url = f"{ADZUNA_BASE_URL}/{country}/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": keywords,
        "where": location,
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, params=params, timeout=10) #requests.get() makes an HTTP GET request to Adzuna's server — exactly like your browser visiting a webpage, but in Python code. The params dictionary gets added to the URL as query parameters automatically by the requests library.
        #timeout=10 — if Adzuna does not respond within 10 seconds, stop waiting and return empty results. Without a timeout, a slow API could freeze your app forever.
        
        response.raise_for_status() #response.raise_for_status() — if Adzuna returns an error code like 401 (unauthorized) or 429 (rate limited), this raises an exception immediately rather than silently returning broken data.
        
        #parsing of the data starts from here   
        data = response.json()#Adzuna returns JSON. .json() converts it to a Python dictionary. data["results"] is a list of job objects. We loop through each and extract the fields we need.

        jobs = []
        for job in data.get("results", []):
            #job.get("company", {}).get("display_name", "Unknown") — company is a nested dictionary inside the job. We get the company dict first with a default of {}, then get display_name from it. This chained .get() prevents crashes if either level is missing.
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")

            if salary_min and salary_max:
                salary = f"₹{int(salary_min):,} - ₹{int(salary_max):,}"
            elif salary_min:
                salary = f"₹{int(salary_min):,}+"
            else:
                salary = "Not specified"

            description = job.get("description", "")
            if len(description) > 300:
                description = description[:300] + "..."

            jobs.append({
                "title": job.get("title", "Unknown Title"),
                "company": job.get("company", {}).get("display_name", "Unknown Company"),
                "location": job.get("location", {}).get("display_name", "Unknown Location"),
                "salary": salary,
                "description": description,
                "apply_url": job.get("redirect_url", ""),
                "created": job.get("created", "")[:10] if job.get("created") else ""
            })

        return jobs
    # error handling 
    # If anything goes wrong — timeout, network error, bad credentials — the function returns an empty list instead of crashing. The UI handles empty results gracefully.
    except requests.exceptions.Timeout:
        print("Adzuna API request timed out")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Adzuna API error: {e}")
        return []

def build_search_keywords(parsed_resume: dict, match_result: dict) -> str:
    """
    Uses Claude to intelligently extract the best job search
    keywords from any resume profile.
    Works for any professional background — PM, developer,
    designer, data scientist, analyst, etc.
    """
    import os
    from anthropic import Anthropic

    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    experience = parsed_resume.get("experience", [])
    skills = parsed_resume.get("skills", [])

    recent_roles = []
    for job in experience[:2]:
        role = job.get("role", "")
        company = job.get("company", "")
        if role:
            recent_roles.append(f"{role} at {company}")

    prompt = f"""You are a job search expert.
Based on this person's experience and skills, what is the
best 2-3 word job search keyword to find relevant jobs?

Recent experience:
{chr(10).join(recent_roles)}

Top skills: {', '.join(skills[:5])}

Rules:
- Return ONLY the keyword phrase — nothing else
- Maximum 3 words
- Use standard job title language recruiters use
- Examples: "Product Manager", "Software Engineer",
  "Data Scientist", "UX Designer", "DevOps Engineer"

Keyword:"""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=20,
        messages=[{"role": "user", "content": prompt}]
    )

    keyword = message.content[0].text.strip()
    keyword = keyword.replace('"', '').replace("'", "").strip()

    return keyword

    

def get_jobs_for_profile(
    parsed_resume: dict,
    match_result: dict,
    country: str = "in"
) -> dict:
    """
    Main function called by the UI.
    Builds keywords from profile and fetches matching jobs.

    Input:
        parsed_resume: from resume parser
        match_result: from JD matcher
        country: "in" for India, "gb" for UK

    Output:
        dictionary with keywords used and list of jobs found
    """

    keywords = build_search_keywords(parsed_resume, match_result)
    print(f"Searching Adzuna for: {keywords}")

    jobs = search_jobs(
        keywords=keywords,
        country=country,
        results_per_page=5
    )

    return {
        "keywords_used": keywords,
        "jobs_found": len(jobs),
        "jobs": jobs
    }


if __name__ == "__main__":
    test_resume = {
        "name": "Vaishali Bhardwaj",
        "experience": [
            {
                "role": "Product Owner / Product Manager",
                "company": "BT Group"
            }
        ]
    }

    test_match = {
        "matched_skills": [
            "AI/ML Product Management",
            "LLM Applications",
            "Product Roadmap",
            "GCP"
        ]
    }

    print("Testing Adzuna Jobs API...")
    print("---")
    result = get_jobs_for_profile(test_resume, test_match)
    print(f"Keywords used: {result['keywords_used']}")
    print(f"Jobs found: {result['jobs_found']}")
    print()

    for i, job in enumerate(result["jobs"], 1):
        print(f"Job {i}:")
        print(f"  Title:    {job['title']}")
        print(f"  Company:  {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Salary:   {job['salary']}")
        print(f"  Posted:   {job['created']}")
        print(f"  Apply:    {job['apply_url']}")
        print()