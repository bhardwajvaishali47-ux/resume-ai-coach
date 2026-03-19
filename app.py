import streamlit as st
import tempfile
import os
from dotenv import load_dotenv
from pipeline import analyze_resume

load_dotenv() # invoke API url key

st.set_page_config(
    page_title = "AI Resume Coach",
    page_icon = "📄",
    layout = "wide"
)

st.title("AI Resume Coach") #Displays a large heading at the top of your page. This is the first thing users see.
st.markdown("Upload your resume and paste a job description to get an instant match analysis powered by Claude AI") #Why explain the app in one sentence? Because when a recruiter visits your app, they need to understand what it does in 3 seconds. Clear, direct description.
st.divider()#Draws a horizontal line across the page. Creates visual separation between the header and the input section below. Small detail but makes the layout look clean and intentiona.

col1, col2 = st.columns(2)
#st.columns(2)-> split the page into 2 columns . This function returns 2 column objects we stored in col1 and col2

with col1:  #The with statement here means — put everything inside this block into column 1.
    st.subheader("Upload Your Resume") #Displays a medium sized heading. Smaller than st.title(), larger than normal text. Used for section labels.
    upload_file = st.file_uploader("Choose your resume PDF" , type=["pdf"] , help ="Upload a text based PDF exported from Word or Google Docs")
    
with col2: #Everything indented under with col2: appears in the right column.
    st.subheader("Paste Your Job Description")
    job_description = st.text_area("Paste the full job description here" , height= 300 , placeholder = "Copy and paste the job description from LinkedIn , Naukri, or any job portal....") # text_area->Creates a multi-line text input box with 4 arguments ->"Paste the full job description here" — the label above the box. | height=300 — how tall the box is in pixels. 300 pixels gives enough space to paste a full job description. |  grey text that appears inside the empty box guiding the user. Disappears when they start typing.
    
st.divider() #Creates a clickable button. Returns True when clicked, False otherwise. You store this in analyse_button — later you check if analyse_button: to know when the user clicked it.


analyse_button = st.button(
    "Analyse my Resume", type = "primary", use_container_width=True
) #type = "primary" -Makes the button blue and prominent — the main action button on the page.
#use_container_width=True ->Makes the button stretch to full width of the page. Looks more professional than a small button.


if analyse_button : #Remember st.button() returns True when clicked. So this entire block runs only when the user clicks the button. If they have not clicked it, Python skips everything inside.
    
    #Before running the expensive API calls, check that the user has provided both inputs.
    #uploaded_file is None — Streamlit sets uploaded_file to None if no file has been uploaded yet.
    #not job_description.strip() — .strip() removes whitespace. If the text area is empty or has only spaces, this is True. not reverses it — so this runs when the job description is empty.
    #st.warning() — shows a yellow warning box on the page.This is called input validation — checking that inputs are valid before processing them.

    if upload_file is None:
        st.warning("Please upload your resume PDF first.")
    elif not job_description.strip():
        st.warning("Please paste a job description first.")
        
    #with st.spinner("..."):Shows an animated spinning indicator with your message while the code inside runs. The spinner disappears automatically when the code finishes.
    #This is critical for user experience. Your pipeline takes 20-30 seconds. Without a spinner the user sees nothing happening and thinks the app is broken. With a spinner they know to wait.

    else:
        with st.spinner("Analysing your resume with Claude AI... This may take 20- 30 seconds."):
            
            
    #This is the bridge between Streamlit's memory and your PDF reader.
    #tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") — creates a temporary file on your disk with a .pdf extension. delete=False means it stays on disk after the with block finishes — you need it to still exist when analyze_resume() reads it.
    #uploaded_file.getvalue() — gets the raw bytes of the uploaded PDF from Streamlit's memory.
    #tmp_file.write(...) — writes those bytes to the temporary file on disk.
    #tmp_path = tmp_file.name — saves the temporary file's path. Looks like /tmp/tmpXXXXXX.pdf.
            with tempfile.NamedTemporaryFile(delete= False, suffix=".pdf") as tmp_file:
                tmp_file.write(upload_file.getvalue())
                tmp_path = tmp_file.name
        
        
        #in this result section -entire pipeline runs here. One line. PDF reading, resume parsing, JD matching    
            result = analyze_resume(tmp_path , job_description)
            os.unlink(tmp_path) #os.unlink(tmp_path)-Deletes the temporary file after analysis is complete. Clean up after yourself. unlink is the Unix term for deleting a file.
            
        if "error" in result:
            st.error(result["error"])
        
     #Stores the result in session_state so it survives the next rerun. Streamlit reruns the entire script on every interaction. Without this, results would disappear the moment the user scrolls or clicks anything.    
        else:
            st.session_state["result"] = result
            st.session_state["analysis_done"] = True # a flag to know whether to show results section.
            
            
            
    if st.session_state.get("analysis_done") : #Checks if analysis has been completed. .get() returns None if key does not exist — no crash. This block only shows after the user has clicked Analyse and results are stored.
        result = st.session_state["result"]
        parsed = result["parsed_resume"]
        match = result["match_result"]
        
        st.divider()
        st.header("Your Analysis Result")
        
        score = match.get("match_score",0)
        st.subheader(f"Match Score: {score}%") #Shows a visual progress bar. Takes a value between 0 and 1. Since your score is 0-100, divide by 100.
        st.progress(score/100)
        
        
        #Loops through the list of matched skills. For each one, displays a line with a green tick emoji. This is how you turn a Python list into a visual list on the page.
        if score >= 75 :
            st.success(" Strong match. You should apply for this role")
        elif score >=50 :
            st.warning("Moderate match. Consider addressing the gaps before applying")
        else:
            st.error("Low match. Significant gaps needs to be addressed")
            
            
        st.divider()
        
        col3 , col4 = st.columns(2)
        
        with col3 : 
            st.subheader("Matched Skills")
            for skill in match .get("matched_skills", []):
                st.markdown(f"✅ {skill}")      
                
                
        with col4:
         st.subheader("Missing Skills")
         for skill in match.get("missing_skills", []):
            st.markdown(f"❌ {skill}")
                
        st.divider()
        
        col5, col6 = st.columns(2)
        
        with col5 :
            st.header("Your Strengths")
            for strength in match.get("strengths",[]):
                st.markdown(f"⭐ {strength}")
                
        with col6:
            st.header("Areas to Improve")
            for gap in match.get("gaps", []):
                st.markdown(f"⚠️ {gap}")
                
        st.divider()
        
        st.subheader("Recommendation")
        st.info(match.get("recommendation", ""))
        
        st.divider()
        
        st.subheader("Your Parsed Resume")
        with st.expander("Click to view full parsed resume data"): # st.expander->Creates a collapsible section. Collapsed by default. User clicks to expand. Used here for the raw JSON data — most users do not need to see it but technical users appreciate it being available.
            st.json(parsed) #st.json->Displays a Python dictionary as formatted, collapsible JSON in the browser. Beautiful out of the box.