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
def onClick(){


}


with gr.Blocks() as main:
    with gr.Row():
        with gr.Column(scale=0.5): # scale relates to proportion of screen taken up
            bt1 = gr.Button("Critial")
            bt2 = gr.Button("Moderate")
            bt3 = gr.Button("Safe")
            bt4 = gr.Button("Discussion")

            bt1.click(
                fn=onClick,
                inputs= ["bt1"],
                outputs=["md1"]

            )
        with gr.Column(scale=2):
            md1 = gr.Markdown("")
        with gr.Column(scale=2):
            btn1 = gr.Button("Button 1")
            btn2 = gr.Button("Button 2")

main.launch()