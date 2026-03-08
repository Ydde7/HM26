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

# --- Helper Logic ---
def get_status_from_pain(pain_level):
    try:
        level = int(pain_level)
        if 1 <= level <= 3: return "Stable"
        elif 4 <= level <= 7: return "Moderate"
        elif 8 <= level <= 10: return "Critical"
        else: return "Discussion"
    except: return "Discussion"

def get_patients_from_csv():
    if not os.path.exists(CSV_FILENAME): return []
    patients = []
    with open(CSV_FILENAME, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 12: 
                patients.append({
                    "name": row[0], "age": row[1], "gender": row[2], 
                    "pain": row[6], "status": get_status_from_pain(row[6]),
                    "symptoms": row[8:11], "substances": row[11:]
                })
    return patients

def filter_data(status):
    all_p = get_patients_from_csv()
    if status == "All": return all_p
    return [p for p in all_p if p["status"] == status]

def format_patient_list(patient_list):
    if not patient_list: return "No patients found."
    return "\n".join([f"• **{p['name']}** | {p['gender']} | Pain: {p['pain']}" for p in patient_list])

# def save_to_csv(data):
#     lines = data.strip().split('\n')
    
#     with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         for line in lines:
#             reader = csv.reader([line])
#             for row in reader:
#                 writer.writerow(row)
#     return f"Successfully appended to {CSV_FILENAME}"

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

        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(list(csv.reader([csv_line]))[0])
        return csv_line, "Saved", gr.Column(visible=False), gr.Column(visible=True)

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
        # LEFT: Vertical Patient List
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### Patients")
            b_all = gr.Button("All")
            b_crit = gr.Button("Critical")
            b_mod = gr.Button("Moderate")
            b_stab = gr.Button("Stable")
            b_disc = gr.Button("Discussion")
            p_display = gr.Markdown(format_patient_list(get_patients_from_csv()))

        # MIDDLE: Chat
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Clinical Communication", height=500)
            msg = gr.Textbox(placeholder="Type message...")
            msg.submit(lambda x: [["", x]], msg, chatbot)

        # RIGHT: Extraction & Tasks
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            with gr.Column(visible=True) as result_col:
                pdf_input = gr.File(label="Upload PDF")
                btn = gr.Button("Extract & Save Data", variant="primary")
            
            with gr.Column(visible=False) as task_col:
                gr.Markdown("### Required Tasks")
                task_input = gr.Textbox(label="New Task")
                add_task = gr.Button("Add Task")
                check_group = gr.CheckboxGroup([], label="Tasks")
                clear_btn = gr.Button("Clear All")
            
            line_output = gr.Textbox(label="Last Output", lines=2)
            status_output = gr.Label(label="Status")

    # Interactions
    b_all.click(lambda: format_patient_list(filter_data("All")), None, p_display)
    b_crit.click(lambda: format_patient_list(filter_data("Critical")), None, p_display)
    b_mod.click(lambda: format_patient_list(filter_data("Moderate")), None, p_display)
    b_stab.click(lambda: format_patient_list(filter_data("Stable")), None, p_display)
    b_disc.click(lambda: format_patient_list(filter_data("Discussion")), None, p_display)
    
    btn.click(form_to_csv_line, inputs=pdf_input, outputs=[line_output, status_output, result_col, task_col])
    add_task.click(lambda t, g: gr.CheckboxGroup(choices=g + [t]), [task_input, check_group], check_group)
    clear_btn.click(lambda: gr.CheckboxGroup(choices=[]), None, check_group)

demo.launch()