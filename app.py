import streamlit as st
import re
import pdfplumber
import openai
import json
import tempfile
import os
import base64
import time

# Set up your OpenAI API key
openai.api_key = "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"

# Function to extract layouts using pdfplumber
def extract_layouts(pdf_path):
    layouts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            layouts.append(page.extract_text())
    return layouts

# Function to process PDF and get answers using OpenAI
def process_pdf_and_get_answers(text):
    # Use the extracted text as context for question answering
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that extracts information."},
        {"role": "user", "content": text}
    ]
    
    # List of questions to ask the assistant
    questions = [
        "Please understand the text properly then give me an answer properly for the following questions: "
        "Please extract details like Invoice Number, Invoice Date, Order Number, Product names, Quantities, Prices, and Total Amount in table format",
        "Save these details like Invoice Number, Invoice Date, Order Number, Products in a JSON file",
    ]
    
    answers = []

    # Iterate through questions and get responses from the model
    gptTime = time.time()
    for question in questions:
        conversation.append({"role": "user", "content": question})
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        assistant_reply = response['choices'][0]['message']['content']
        answers.append((question, assistant_reply))
        conversation.pop()  # Remove the user message for the next iteration
    
    print('gptTime is taken ------ ', time.time() - gptTime, '\n\n\n')
    
    return answers

# Function to extract JSON content from the answer using regex
def extract_json_format_from_answer(answer):
    # Use regex to find and extract the entire JSON format

    try: 
        json_text = answer.split('''```''')[1][len('json\n'):-1].replace('\n', '')
        json_matches = json.loads(json_text)
        return json_matches
    except:
        print(" The text seems to be corrupted or no json like structure in it ")
        return None

# Streamlit UI
def main():
    st.sidebar.image("Websynergies-logo.png", caption="powered by")
    st.title("Invoice Invader")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # Process the uploaded PDF and get answers
        with st.spinner("File is in process..."):
            uploaded_file_path = "uploaded_pdf.pdf"
            with open(uploaded_file_path, "wb") as f:
                f.write(uploaded_file.read())
            
            pdfTime = time.time()
            uploaded_layouts = extract_layouts(uploaded_file_path)
            uploaded_text = "\n".join(uploaded_layouts)
            print('pdfTime is taken ------ ', time.time() - pdfTime, '\n\n\n')

            answers = process_pdf_and_get_answers(uploaded_text)

            for question, answer in answers:
                st.write(answer)
            
            # Extract JSON content from the answers
            extracted_json = extract_json_format_from_answer(answers[-1][1])  # Get the last answer
            print(answers)
            if extracted_json:
                with open('invoice.json', 'w') as file:
                    json.dump(extracted_json, file)
                
                # Create a download button for the JSON data

                with open('invoice.json', 'r') as file:
                    st.download_button(
                        label="Download Extracted JSON",
                        data=file,
                        key="download-json",
                        file_name="extracted_data.json"  # Specify the file name with .json extension
                    )

if __name__ == "__main__":
    main()