import streamlit as st
from dotenv import load_dotenv
import os
import openai
from langchain.prompts import PromptTemplate
import pandas as pd

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["text", "subject", "tone", "num_questions"],
    template=(
        "Generate {num_questions} multiple-choice questions based on the following text.\n\n"
        "Text: {text}\n\n"
        "Subject: {subject}\n\n"
        "Difficulty: {tone}\n\n"
        "Output the result in the following JSON format:\n"
        "{{\n"
        "    \"questions\": [\n"
        "        {{\n"
        "            \"mcq\": \"multiple choice question\",\n"
        "            \"options\": {{\n"
        "                \"a\": \"choice here\",\n"
        "                \"b\": \"choice here\",\n"
        "                \"c\": \"choice here\",\n"
        "                \"d\": \"choice here\"\n"
        "            }},\n"
        "            \"correct\": \"correct answer\"\n"
        "        }},\n"
        "        ... (repeat for each question)\n"
        "    ]\n"
        "}}"
    )
)

# Define a function to generate MCQs
def generate_mcqs(text, subject, tone, num_questions):
    prompt = prompt_template.format(text=text, subject=subject, tone=tone, num_questions=num_questions)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=2000,
        temperature=0.7
    )
    return response.choices[0].message["content"].strip()

# Define a function to parse the JSON response
def parse_mcqs(mcq_json):
    import json
    mcq_data = json.loads(mcq_json)
    return mcq_data['questions']

# Streamlit app layout
st.title("MCQ Generator")

# File upload
uploaded_file = st.file_uploader("Upload a text file", type="txt")
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    st.text_area("Uploaded Text", text, height=300)
    
    subject = st.text_input("Enter the subject")
    tone = st.selectbox("Select the difficulty level", ["Simple", "Medium", "Complex"])
    num_questions = st.number_input("Enter the number of MCQs", min_value=1, step=1)

    if st.button("Generate MCQs"):
        mcq_json = generate_mcqs(text, subject, tone, num_questions)
        mcqs = parse_mcqs(mcq_json)

        # Display MCQs in a table
        mcq_list = []
        for i, mcq in enumerate(mcqs, 1):
            options = mcq['options']
            mcq_list.append({
                "Question": mcq['mcq'],
                "Option A": options["a"],
                "Option B": options["b"],
                "Option C": options["c"],
                "Option D": options["d"],
                "Correct Answer": mcq['correct']
            })
        
        df_mcqs = pd.DataFrame(mcq_list)
        st.table(df_mcqs)

        # Provide a review mechanism
        reviews = []
        for i in range(num_questions):
            review = st.selectbox(f"Review for Question {i+1}", ["Good", "Average", "Poor"], key=f"review_{i}")
            reviews.append(review)
        
        if st.button("Submit Reviews"):
            review_summary = {f"Question {i+1}": reviews[i] for i in range(num_questions)}
            st.json(review_summary)