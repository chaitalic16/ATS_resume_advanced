from dotenv import load_dotenv
load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
from docx import Document  # For reading DOC files
import PyPDF2  # For extracting text from PDF files

# Configure API key for Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit App
st.set_page_config(page_title="Resume Extractor")
st.title("ATS Tracking System")

# Inline CSS for styling
custom_css = """
<style>
/* General App Background and Layout */
body {
    font-family: 'Arial', sans-serif;
}
.stApp {
    background: linear-gradient(to right, rgb(93, 20, 185), rgb(229, 77, 78));
    padding: 0;
}

/* Main header styling */
h1 {
    color: #fff;
    text-align: center;
    margin: 20px 0;
}

/* Job Description label */
.stTextArea label p{
    font-family: 'Arial', sans-serif;
    color: #ffffff !important; /* Force the color change */
    font-size: 1.4em !important;
}

/* File uploader label */
.stFileUploader label {
    font-family: 'Arial', sans-serif;
    color: #000;
    font-size: 1.2em;
}

/* Style the file uploader */
.stFileUploader {
    border: 2px dashed rgb(58, 11, 133);
    border-radius: 10px;
    padding: 20px;
    background-color: #f4f4f4;
}

/* Button container styling */
.button-container {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

/* Button styling */
button, .stButton>button {
    background-color: rgb(58, 11, 133);
    color: #fff;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 1.2em;
    cursor: pointer;
}

button:hover, .stButton>button:hover {
    background-color: rgb(50, 10, 115);
}

/* Output page styling */
.output-container {
    background-color: #fff;   /* White background for output */
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin: 20px auto;
    padding: 80px;  /* Padding for the inner content */
    max-width: 800px;  /* Limit width for better readability */
}


/* Subheading styling for output sections */
.stSubheader {
    color: rgb(255, 223, 0);
    font-size: 2em;
    text-align: center;
}
</style>
"""

# Apply custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Function to get a response from Gemini model
def get_gemini_response(input_text, doc_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, doc_content[0], prompt])
    return response.text

# Function to extract text from a DOC file
def input_doc_setup(uploaded_file):
    doc = Document(uploaded_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Function to extract text from a PDF file
def input_pdf_setup(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in range(len(reader.pages)):
        full_text += reader.pages[page].extract_text()
    return full_text

# Input Job Description
input_text = st.text_area("Job Description: ", key="input")

# File Uploader for both PDF and DOC
uploaded_file = st.file_uploader("Upload your resume (PDF or DOC)...", type=["pdf", "docx"])

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    st.markdown(f"<span style='color: white; font-size: 16px;'>{file_type.upper()} File Uploaded Successfully</span>", unsafe_allow_html=True)

# Button container to align the buttons side by side
st.markdown('<div class="button-container">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    submit1 = st.button("Tell Me About the Resume")

with col2:
    submit3 = st.button("Percentage Match")

st.markdown('</div>', unsafe_allow_html=True)

# Input prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements. 
Compare the years of experience mentioned in the resume with the requirements in the job description.
start directly with overall evaluation,dont include ## lines.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Give me the percentage match for the resume,
the percentage should display in bold and greater numbers so that it can visible to user.
First, the output should come as a percentage, followed by missing technologies, also compare the years of experience mentioned in the resume 
with those required in the job description and indicate if they meet the expectations and lastly conclusion.
"""

# Store responses
if submit1 or submit3:
    if uploaded_file is not None:
        if file_type == "pdf":
            resume_content = input_pdf_setup(uploaded_file)  # Extract content from PDF
        elif file_type == "docx":
            resume_content = input_doc_setup(uploaded_file)  # Extract content from DOC
        
        # Generate AI response
        if submit1:
            response = get_gemini_response(input_text, [resume_content], input_prompt1)
            st.markdown("""
               <div class='output-container'>
            <h3>Evaluation Of Complete Resume</h3>
            <p>{}</p>
        </div>
        """.format(response), unsafe_allow_html=True)
            if st.button("Back to Home"):
                st.session_state.clear()# Clear session state to reset

        elif submit3:
            response = get_gemini_response(input_text, [resume_content], input_prompt3)
            st.markdown("""
               <div class='output-container'>
            <h3>Resume Evaluation With Percentage</h3>
            <p>{}</p>
        </div>
        """.format(response), unsafe_allow_html=True)
            
            if st.button("Back to Home"):
                st.session_state.clear()  # Clear session state to reset
    else:
        st.write("Please upload the resume")


