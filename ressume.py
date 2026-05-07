import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from groq import Groq

# Load environment variables from .env
load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")
st.title("AI Resume Analyzer")
st.write("Analyze your resume against a job description using AI")

# Try .env first, then Streamlit secrets
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("groq_api_key")

if not groq_api_key:
    st.error("Groq API key not found. Please set it in .env or Streamlit secrets.")
else:
    uploaded_file = st.file_uploader("Upload resume file", type=["pdf"])
    job_description = st.text_area("Paste Job Description")

    if st.button("Analyze Resume"):
        if not uploaded_file:
            st.error("Please upload a file")
        elif not job_description:
            st.error("Please enter job description")
        else:
            with open("temp_resume.pdf", "wb") as f:
                f.write(uploaded_file.read())

            reader = PdfReader("temp_resume.pdf")
            resume_text = " ".join([page.extract_text() or "" for page in reader.pages])

            client = Groq(api_key=groq_api_key)

            prompt = f"""
            You are an AI Resume Analyzer.

            Compare the following resume with the job description.

            Resume:
            {resume_text}

            Job Description:
            {job_description}

            Provide:
            1. Match Score (in percentage)
            2. Missing Skills
            3. Strengths
            4. Weaknesses
            5. Suggestions to improve resume
            6. Improved bullet points for resume
            """

            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.choices[0].message.content
                st.subheader("Analysis Result")
                st.write(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
