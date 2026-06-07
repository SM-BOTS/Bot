from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Templates configuration
templates = Jinja2Templates(directory="templates")

# Aapka MongoDB ka link yahan aayega
MONGO_URI = "mongodb+srv://gxmon239:f4l7bKrhka3Fh2cV@cluster0.qmblwql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["bypass_protector"]
links_col = db["links"]

# Home page par agar koi jaye toh use normal message dikhe (404 na aaye)
@app.get("/")
async def home():
    return {"status": "Server is running smoothly!"}

# Yeh aapka main bypass-proof page hai
@app.get("/visit", response_class=HTMLResponse)
async def visit_page(request: Request, id: str):
    link_data = await links_col.find_one({"_id": id})
    if not link_data:
        return HTMLResponse(content="<h2>Link Expired ya Invalid hai!</h2>", status_code=404)
    
    return templates.TemplateResponse("index.html", {"request": request, "link_id": id})

@app.post("/redirect")
async def handle_redirect(link_id: str = Form(...)):
    link_data = await links_col.find_one({"_id": link_id})
    if not link_data:
        raise HTTPException(status_code=404, detail="Session Expired")
    
    # Anti-Bypass logic: click hote hi link delete
    await links_col.delete_one({"_id": link_id})
    
    return RedirectResponse(url=link_data["original_url"], status_code=303)
