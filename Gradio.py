from State import run_agent
import gradio as gr

iface = gr.Interface(
    fn=run_agent,
    inputs=["text"],
    outputs="text",
    live=False,
)
iface.launch(share=True)
