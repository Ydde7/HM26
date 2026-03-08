import gradio as gr
import random

# 0 = main ; 1 = patient view ; 3 = ?
screen = 0

with gr.Blocks() as main:
    with gr.Row():
        title = gr.Markdown("Patient Check in")
    with gr.Row():
        with gr.Column(scale=1): # scale relates to proportion of screen taken up
            bt1 = gr.Button("Critial")
            bt2 = gr.Button("Moderate")
            bt3 = gr.Button("Safe")
            bt4 = gr.Button("Discussion")
            back = gr.Button("Back", visible=False)

        with gr.Column(scale=3):
            md1 = gr.Markdown("")
            html = gr.HTML(format())
        with gr.Column(scale=1):
            btn1 = gr.Button("Button 1")
            btn2 = gr.Button("Button 2")

        # --- Functions ---
        def disc_click(value: str | None):
            screen = 1
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
        
        def back_click(value: str | None):
            screen = 0
            bt1.visible = True
            bt2.visible = True
            bt3.visible = True
            bt4.visible = True
            md1.visible = True
            back.visible = False
            
            return{
                bt1: gr.Button(visible=True),
                bt2: gr.Button(visible=True),
                bt3: gr.Button(visible=True),
                bt4: gr.Button(visible=True),
                md1: gr.Markdown(visible=True),
                back: gr.Button(visible=False)
            }
   
        def critical_click(value: str | None):
            if (bt1.visible == False):
                bt1.visible = True
                return {
                    bt1: gr.Button("Critical"),
                    bt2: gr.Button(visible=True),
                    bt3: gr.Button(visible=True),
                    bt4: gr.Button(visible=True),
                    md1: gr.Markdown("We are back!")
                }
            else:
                bt1.visible = False
                return {
                    bt1: gr.Button("Back"),
                    bt2: gr.Button(visible=False),
                    bt3: gr.Button(visible=False),
                    bt4: gr.Button(visible=False),
                    md1: gr.Markdown(str(bt2.visible))
                }
            
        def mod_click(value: str | None):
            if (bt2.visible == False):
                bt2.visible = True
                return {
                    bt1: gr.Button(visible=True),
                    bt2: gr.Button("Moderate"),
                    bt3: gr.Button(visible=True),
                    bt4: gr.Button(visible=True),
                    md1: gr.Markdown("temp")
                }
            else:
                bt2.visible = False
                return {
                    bt1: gr.Button(visible=False),
                    bt2: gr.Button("Back"),
                    bt3: gr.Button(visible=False),
                    bt4: gr.Button(visible=False),
                    md1: gr.Markdown(str(bt2.visible))
                }
            
        def safe_click(value: str | None):
            if (bt3.visible == False):
                bt3.visible = True
                return {
                    bt1: gr.Button(visible=True),
                    bt2: gr.Button(visible=True),
                    bt3: gr.Button("Safe"),
                    bt4: gr.Button(visible=True),
                    md1: gr.Markdown("Also Works!")
                }
            else:
                bt3.visible = False
                return {
                    bt1: gr.Button(visible=False),
                    bt2: gr.Button(visible=False),
                    bt3: gr.Button("Back"),
                    bt4: gr.Button(visible=False),
                    md1: gr.Markdown("temp")
                }

        # --- Click handlers ---

        bt1.click(fn=critical_click,
            inputs= [bt1],
            outputs=[bt1, bt2, bt3, bt4, md1]
        )

        bt2.click(fn=mod_click,
            inputs=[bt2],
            outputs=[bt1, bt2, bt3, bt4, md1]
        )

        bt3.click(fn=safe_click,
            inputs=[bt3],
            outputs=[bt1, bt2, bt3, bt4, md1]
        )

        bt4.click(fn=disc_click,
            inputs=[bt4],
            outputs=[bt1, bt2, bt3, bt4, md1, back]
        )

        back.click(fn=back_click,
            inputs=[back],
            outputs=[bt1, bt2, bt3, bt4, md1, back]
        )

main.launch()