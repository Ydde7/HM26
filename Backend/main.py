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
    
MSTAT_css = """
    .container { background-color: #36393f !important; color: #dcddde !important; }
    .sidebar-panel { background-color: #2f3136 !important; padding: 15px !important; border-radius: 0 !important; }
    .chat-window { background-color: #36393f !important; }
    h3 { color: #8e9297 !important; text-transform: uppercase; font-size: 12px !important; }
    """

with gr.Blocks(theme=gr.themes.Base(), css=MSTAT_css) as demo:
    with gr.Row(elem_classes="container"):
        
        # 1. Left Sidebar: Patient List
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### Attendees")
            gr.Markdown("• **John Doe** (Bed 04)\n• **Jane Smith** (Triage)")
            gr.Markdown("### Shift Stats")
            gr.Label({"Critical": 1, "Stable": 5})

        # 2. Middle: Discord Chat Window
        with gr.Column(scale=3, elem_classes="chat-window"):
            chatbot = gr.Chatbot(label="Clinical Communication", height=500)
            msg = gr.Textbox(placeholder="Type message to team...")
            msg.submit(lambda x: [["", x]], msg, chatbot)

        # 3. Right Sidebar: PDF Extraction + Tasks
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### PDF Extraction")
            pdf_input = gr.File(label="Upload PDF")
            btn = gr.Button("Extract & Save Data", variant="primary")
            line_output = gr.Textbox(label="Last Extraction", lines=3)
            status_output = gr.Label(label="File Status")
            
            gr.Markdown("### Required Actions")
            checklist = gr.CheckboxGroup(["Administer IV", "Check Vitals", "Update Chart"], label="Tasks")
    btn.click(
        fn=form_to_csv_line, 
        inputs=pdf_input, 
        outputs=[line_output, status_output]
    )

demo.launch()