import os
import json
from dotenv import load_dotenv
# call function from our own created files 
from tools.pdf_reader import extract_text_from_pdf
from chains.resume_parser import parse_resume
from chains.jd_matcher import match_resume_to_job

load_dotenv() #invoke api url


# below is the master function. single entry line for the pipeline.
# two inputs :location of the pdf file on my mac (type string) adn job description as plain text
# output weill be in the form of dictionary 
def analyze_resume (pdf_path : str, job_description : str) -> dict:
    """ Master pipeline function. Connects pdf_reader,resume parser and jd_matcher into one single row.
    
    Input:
    pdfpath : full path to the PDF resume file
    job_description : job description as plain text
    
    Output:
    dictionary containing:
    -parsed_resume : strucutred resume data
    -match_result : score, gaps, strenghts, recommendation
    """
    
    #calls pdf_reader.py function , pass the file path , get plain text
    #open the pdf with pdf plumber, loops through evbery page , extract text    , cleans up encoding issue(cid:127), return clean text
    print("Step 1 of 3: Reading your PDF resume...")
    resume_text = extract_text_from_pdf(pdf_path)
    
    
    #Error handling - if the PDF is image based  and nothing extracts ,function returns a string starting with ERROR.
    #startswith("ERROR:") checks if the returned text begins with those exact characters. If yes — something went wrong with the PDF. Instead of crashing the entire pipeline, you stop gracefully and return a dictionary with an error message.
    #return {"error": resume_text} — returns immediately. The function stops here if there is an error. Steps 2 and 3 never run.
    if resume_text.startswith("ERROR"):
        print(resume_text)
        return {"error" : resume_text}
    
    
    # parsing the resume 
    #Calls your resume_parser.py chain. Passes the raw text. Gets back a structured dictionary.parsed_resume.get('skills', [])
    #.get() is a safe way to access a dictionary key. It takes two arguments :-skills , a deafult value if the key does not exist[]
    
    #Why use .get() instead of parsed_resume['skills']?  If for any reason Claude did not return a skills field, parsed_resume['skills'] would crash with a KeyError. parsed_resume.get('skills', []) returns an empty list instead. Safe, no crash.
    
    #len() counts how many items are in the list. So len(parsed_resume.get('skills', [])) tells you how many skills were found.
    
    print(f"Done. Extracted{len(resume_text)} characters.") #The f before the quote makes this an f-string. Whatever is inside {} gets evaluated and inserted into the string. So if 12 skills were found, this prints: Done. Found 12 skills

    print()
    
    print("Step 2 of 3: Parsing resume with Claude...")
    parsed_resume = parse_resume(resume_text)
    print(f"Done. Found {len(parsed_resume.get('skills',[]))} skills  ")
    print(f"Done. Found {len(parsed_resume.get('experience', []))} jobs")
    print()
    
    # Calls your jd_matcher.py chain. Passes two things — the raw resume text AND the job description. Gets back match analysis.
    print("Step 3 of 3 : Matching against job description ...")
    match_result = match_resume_to_job(resume_text, job_description)
    print(f"Done. Match score : {match_result.get('match_score',0)}%") # safely gets the score. Default is 0 if not found.
    print()
    
    return {
        "parsed_resume" : parsed_resume,
        "match_result" : match_result
    }
    
    

    
if __name__ == "__main__":
        PDF_PATH = "Vaishali_Bhardwaj_ProductManager_AI.pdf"
        JD_FILE = "test_job_description_aipm.txt"
        
        with open(JD_FILE, "r") as f: #Opens the job description text file and reads it into a string. The job description goes in as text, not a file path — because jd_matcher.py expects plain text, not a file to open.
            job_description = f.read()
            
        print("=" * 40) #Creates a visual separator line of 40 equals signs. Makes the terminal output organised and readable.
        print("RESUME ANALYSIS PIPELINE")
        print("=" * 40)
        print()
        
        result = analyze_resume(PDF_PATH , job_description)
        
        if "error"  not in result:
            print()
            print("=" * 40) 
            print("YOUR PARSED RESUME")
            print("=" * 40)
            print(json.dumps(result["parsed_resume"], indent =2))
            print()
            print("=" * 40)
            print("YOUR MATCH ANALYSIS")
            print("=" * 40)
            print(json.dumps(result["match_result"], indent =2))
        