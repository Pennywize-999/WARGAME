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

@app.get("/internal", response_class=HTMLResponse)
async def internal():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>INTERNAL SYSTEM NOTICE</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <hr>
            <h2>SEATTLE PUBLIC SCHOOL DISTRICT</h2>
            <h3>COMPUTER SERVICES</h3>
            <hr>
            <br>
            <div class="center-text">INTERNAL SYSTEM NOTICE</div>
            <br>
            <hr>
            <br>
            <p>REMOTE TERMINAL SERVICES</p>
            <br>
            <p>Datanet maintenance is scheduled during</p>
            <p>the next service period.</p>
            <br>
            <p>AUTHORIZED PERSONNEL ONLY.</p>
            <br>
            <hr>
            <br>
            <p>REFERENCE:</p>
            <p class="indent">COMPUTER SERVICES MEMORANDUM 83-17</p>
            <br>
            <hr>
            <br>
            <p class="center-text">COMPUTER SERVICES DEPARTMENT</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)

@app.get("/archives", response_class=HTMLResponse)
async def archives():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CENTRAL RECORDS ARCHIVE</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <hr>
            <h2>SEATTLE PUBLIC SCHOOL DISTRICT</h2>
            <h3>CENTRAL RECORDS ARCHIVE</h3>
            <hr>
            <br>
            <div class="center-text">ARCHIVE INDEX</div>
            <br>
            <hr>
            <br>
            <p class="indent">1981</p>
            <p class="indent">1982</p>
            <p class="indent">1983</p>
            <br>
            <hr>
            <br>
            <p>SECTIONS:</p>
            <p class="indent">COMPUTER SERVICES</p>
            <p class="indent">ADMINISTRATION</p>
            <p class="indent">TRANSPORTATION</p>
            <p class="indent">PERSONNEL</p>
            <br>
            <hr>
            <br>
            <p class="center-text">ACCESS RESTRICTED</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)

@app.get("/records", response_class=HTMLResponse)
async def records():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SYSTEM RECORD</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <hr>
            <h2>SEATTLE PUBLIC SCHOOL DISTRICT</h2>
            <h3>COMPUTER SERVICES</h3>
            <hr>
            <br>
            <div class="center-text">SYSTEM RECORD</div>
            <br>
            <hr>
            <br>
            <p>TERMINAL NETWORK:</p>
            <p class="indent">DISTRICT DATANET</p>
            <br>
            <p>REMOTE ACCESS:</p>
            <p class="indent">AUTHORIZED</p>
            <br>
            <p>SYSTEM STATUS:</p>
            <p class="indent">OPERATIONAL</p>
            <br>
            <hr>
            <br>
            <p>RECORD NO:</p>
            <p class="indent">CS-83-041</p>
            <br>
            <hr>
            <br>
            <p class="center-text">AUTHORIZED PERSONNEL ONLY</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)

@app.get("/personnel", response_class=HTMLResponse)
async def personnel():
    content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PERSONNEL DIRECTORY</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <hr>
            <h2>SEATTLE PUBLIC SCHOOL DISTRICT</h2>
            <h3>COMPUTER SERVICES</h3>
            <hr>
            <br>
            <div class="center-text">PERSONNEL DIRECTORY</div>
            <br>
            <hr>
            <br>
            <p>SYSTEMS ADMINISTRATION</p>
            <br>
            <p>FALKEN, STEPHEN</p>
            <p class="indent">RESEARCH CONSULTANT</p>
            <br>
            <p>COMPUTER SERVICES DEPARTMENT</p>
            <br>
            <hr>
            <br>
            <p class="center-text">AUTHORIZED ACCESS REQUIRED</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=content)
