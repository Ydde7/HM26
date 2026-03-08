import gradio as gr
import random


# print(gr.__version__);
def hi():
    print("Welcome back!")

# demo = gr.Interface(
#     fn = hi;
#     inputs= ["text"]
#     outputs=["text"]

# )

with gr.Blocks() as main:
    with gr.Row():
        with gr.Column(scale=1): # scale relates to proportion of screen taken up
            bt1 = gr.Button("Critial")
            bt2 = gr.Button("Moderate")
            bt3 = gr.Button("Safe", visible=False)
            bt4 = gr.Button("Discussion")

            back = gr.Button("Back", visible="hidden")


        with gr.Column(scale=2):
            md1 = gr.Markdown("")
        with gr.Column(scale=2):
            btn1 = gr.Button("Button 1")
            btn2 = gr.Button("Button 2")


        def visual(value: str | None):

            if (bt2.visible == False):
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



        bt1.click(
            fn=visual,
            inputs= [bt1],
            outputs=[md1, bt2, bt3]
        )

main.launch()