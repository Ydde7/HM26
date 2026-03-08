import os
import csv
import gradio as gr
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("API_KEY"))
CSV_FILENAME = "medical_data.csv"

# --- Backend Logic ---
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
    with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 12: 
                patients.append({
                    "name": row[0], "age": row[1], "gender": row[2], 
                    "pain": row[6], "status": get_status_from_pain(row[6])
                })
    return patients

def filter_data(status):
    all_p = get_patients_from_csv()
    if status == "All": return all_p
    return [p for p in all_p if p["status"] == status]

def format_patient_list(patient_list):
    if not patient_list: return "No patients found."
    return "\n".join([f"• **{p['name']}** | {p['gender']} | Pain: {p['pain']}" for p in patient_list])

def form_to_csv_line(file):
    if file is None: return "Upload a PDF.", "Error", gr.Column(visible=True), gr.Column(visible=False)
    with open(file.name, "rb") as f: pdf_data = f.read()
    
    prompt = "Extract info into 1 CSV line: Name,Age,Gender,Status,Date,PainDesc,PainLevel,SymptomLen,BinaryBits,PriorSurgery,Pills,Tobacco,Alcohol,Drug,Substances. No headers/backticks."
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            config=types.GenerateContentConfig(system_instruction=prompt, temperature=0.1),
            contents=[types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"), "Extract data."]
        )
        csv_line = response.text.strip().replace("`", "")
        with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(list(csv.reader([csv_line]))[0])
        return csv_line, "Saved", gr.Column(visible=False), gr.Column(visible=True)
    except Exception as e:
        return f"Error: {str(e)}", "Failed", gr.Column(visible=True), gr.Column(visible=False)

# --- UI Setup ---
MSTAT_css = """
    .container { background-color: #36393f !important; color: #dcddde !important; }
    .sidebar-panel { background-color: #2f3136 !important; padding: 15px !important; }
    .btn-vertical { display: block !important; width: 100% !important; margin-bottom: 5px !important; }
    h3 { color: #8e9297 !important; text-transform: uppercase; font-size: 12px !important; }
    """

with gr.Blocks(theme=gr.themes.Base(), css=MSTAT_css) as demo:
    with gr.Row(elem_classes="container"):
        # LEFT: Vertical Patient List
        with gr.Column(scale=1, elem_classes="sidebar-panel"):
            gr.Markdown("### Patients")
            # Buttons now use vertical styling
            b_all = gr.Button("All", elem_classes="btn-vertical")
            b_crit = gr.Button("Critical", elem_classes="btn-vertical")
            b_mod = gr.Button("Moderate", elem_classes="btn-vertical")
            b_stab = gr.Button("Stable", elem_classes="btn-vertical")
            b_disc = gr.Button("Discussion", elem_classes="btn-vertical")
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
                # Using a function to handle the empty state correctly
                check_group = gr.CheckboxGroup([], label="Tasks")
                clear_btn = gr.Button("Clear All")
            
            line_output = gr.Textbox(label="Last Output", lines=2)
            status_output = gr.Label(label="Status")

    # --- Interactions ---
    b_all.click(lambda: format_patient_list(filter_data("All")), None, p_display)
    b_crit.click(lambda: format_patient_list(filter_data("Critical")), None, p_display)
    b_mod.click(lambda: format_patient_list(filter_data("Moderate")), None, p_display)
    b_stab.click(lambda: format_patient_list(filter_data("Stable")), None, p_display)
    b_disc.click(lambda: format_patient_list(filter_data("Discussion")), None, p_display)
    
    btn.click(form_to_csv_line, inputs=pdf_input, outputs=[line_output, status_output, result_col, task_col])
    
    # Robust task addition: ensures we don't crash if the group is empty
    def add_task_logic(new_task, current_tasks):
        if current_tasks is None: current_tasks = []
        return gr.CheckboxGroup(choices=current_tasks + [new_task])

    add_task.click(add_task_logic, [task_input, check_group], check_group)
    clear_btn.click(lambda: gr.CheckboxGroup(choices=[]), None, check_group)

demo.launch()