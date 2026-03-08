import gradio as gr
import random

# 0 = main ; 1 = patient view ; 3 = ?
screen = 0


# print(gr.__version__);
def hi():
    print("Welcome back!")

with gr.Blocks() as main:
    with gr.Row():
        title = gr.Markdown("#Patient Check in")
    with gr.Row():
        with gr.Column(scale=1): # scale relates to proportion of screen taken up
            bt1 = gr.Button("Critial")
            bt2 = gr.Button("Moderate")
            bt3 = gr.Button("Safe")
            bt4 = gr.Button("Discussion")

            # Hidden Elements
            back = gr.Button("Back")
            back.unrender()

        with gr.Column(scale=3):
            md1 = gr.Markdown("")
        with gr.Column(scale=1):
            btn1 = gr.Button("Button 1")
            btn2 = gr.Button("Button 2")

        # --- Functions ---
        def disc_click(value: str | None):

            bt1.visible = False
            bt2.visible = False
            bt3.visible = False
            bt4.visible = False
            md1.visible = False
            back.visible = True
            # Hide  / Show values

            return {
                bt1: gr.Button(visible=False),
                bt2: gr.Button(visible=False),
                bt3: gr.Button(visible=False),
                bt4: gr.Button(visible=False),
                md1: gr.Markdown(visible=False),
                back: gr.Button(visible=True)
            }

            
        def visual(value: str | None):

            if (bt2.visible == False):
                bt2.visible = True
                return {
                    bt2: gr.Button(visible=True),
                    md1: gr.Markdown("We are back!")
                }
            else:
                bt2.visible = False
                return {
                    bt2: gr.Button(visible=False),
                    bt3: gr.Button(visible=True),
                    md1: gr.Markdown(str(bt2.visible))
                }

        # def back()
        # --- Click handlers ---

        bt1.click(
            fn=visual,
            inputs= [bt1],
            outputs=[md1, bt2, bt3]
        )

        bt4.click(
            fn=disc_click,
            inputs=[bt3],
            outputs=[bt1, bt2, bt3, bt4, md1, back]
        )

main.launch()