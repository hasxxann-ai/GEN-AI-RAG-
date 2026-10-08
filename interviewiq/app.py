from fastapi import FastAPI
import gradio as gr
from ui.gradio_ui import build_ui
import uvicorn
import os
from dotenv import load_dotenv
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI(title="InterviewIQ API")

@app.get("/")
def read_root():
    return HTMLResponse('<h1>InterviewIQ is running. <a href="/gradio">Go to UI</a></h1>')

# Mount Gradio
demo = build_ui()
app = gr.mount_gradio_app(app, demo, path="/gradio")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
