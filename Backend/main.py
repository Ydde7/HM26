import os
import csv
from dotenv import load_dotenv
import gradio as gr
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("API_KEY")
client = genai.Client(api_key=api_key)

CSV_FILENAME = "medical_data.csv"
def save_to_csv(data):
    lines = data.strip().split('\n')
    
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for line in lines:
            reader = csv.reader([line])
            for row in reader:
                writer.writerow(row)
    return f"Successfully appended to {CSV_FILENAME}"

def form_to_csv_line(file):
    if file is None:
        return "Please upload a PDF file."
    
    with open(file.name, "rb") as f:
        pdf_data = f.read()

    
    prompt = (
        """
        You are a medical data extractor. Convert the provided medical notes into 1 specific CSV lines.
        Follow these formatting rules strictly:
        part 1: Name,Age,Gender(F/M/O),Status(0/1),Date
        part 2: Pain Description(or Null),Pain Level(number only),Symptom Length
        part 3: 8 binary digits for treated conditions (e.g., 1,0,1,0,0,0,1,1),Prior Surgery Sentence,Pills Sentence
        part 4: Tobacco(0/1),Alcohol(0/1),Drug(0/1),Substances Used Sentence

        Do not include headers, explanations, or triple backticks. Just add these 4 parts into 1 line so it could be more readable for the machine.
        """
    )
    try:
        # 3. Pass everything into the generate_content call
        response = client.models.generate_content(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(
                system_instruction=prompt,
                temperature=0.1,
            ),
            contents=[
                types.Part.from_bytes(
                    data=pdf_data,
                    mime_type="application/pdf"
                ),
                "Extract the data from this PDF into the requested CSV format."
            ]
        )
        
        # Clean up the output string
        csv_line = response.text.strip().replace("`", "")

        status_msg = save_to_csv( csv_line)
        
        return  csv_line, status_msg

    except Exception as e:
        return f"An error occurred: {str(e)}", "Failed to save."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("### 📄 MEDICAL PDF TO PERSISTENT CSV")

    with gr.Row():
        with gr.Column():
            pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
            btn = gr.Button("Extract & Save Data", variant="primary")
        
        with gr.Column():
            line_output = gr.Textbox(label="Current Extraction", lines=5)
            status_output = gr.Label(label="File Status")

    btn.click(
        fn=form_to_csv_line, 
        inputs=pdf_input, 
        outputs=[line_output, status_output]
    )

demo.launch()