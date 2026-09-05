from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Seattle Public School District")

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/secret", response_class=HTMLResponse)
async def secret():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>INTERNAL USE ONLY</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <hr>
            <h2>SEATTLE PUBLIC SCHOOL DISTRICT</h2>
            <h3>COMPUTER SERVICES</h3>
            <hr>
            <br>
            <div class="center-text">INTERNAL USE ONLY</div>
            <br>
            <hr>
            <br>
            <p>DISTRICT DATANET ACCESS INFORMATION</p>
            <br>
            <p>ACCOUNT NAME:</p>
            <p class="indent">PRINCIPAL</p>
            <br>
            <p>PASSWORD:</p>
            <p class="indent">PENCIL</p>
            <br>
            <hr>
            <br>
            <p>SYSTEM:</p>
            <p class="indent">SEATTLE PUBLIC SCHOOL DISTRICT DATANET</p>
            <br>
            <p>ACCESS METHOD:</p>
            <p class="indent">REMOTE TERMINAL</p>
            <br>
            <hr>
            <br>
            <p class="center-text">AUTHORIZED PERSONNEL ONLY</p>
            <p class="center-text">COMPUTER SERVICES DEPARTMENT</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)
