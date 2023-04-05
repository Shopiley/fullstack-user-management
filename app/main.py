import uvicorn
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles
from os import path

app = FastAPI() 

parent_dir = path.abspath(path.join(__file__, '..'))
static_dir = path.join(parent_dir, 'templates')
                

app.mount('/', StaticFiles(directory=static_dir, html=True), name='static')

@app.get("/")
async def index(request: Request):
    # Render your HTML template using Jinja2
    template = env.get_template("home.html")
    html_content = template.render()

    # Return the rendered HTML template as a response
    return HTMLResponse(content=html_content, status_code=200)