import os
import requests
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# Templates folder ka path setup
templates = Jinja2Templates(directory="templates")

# Database Connections (Aap chahein toh directly yahan daal sakte hain ya Vercel Environment Variables me)
MONGO_URI = "YOUR_MONGODB_URI_HERE"
CLOUDFLARE_SECRET_KEY = "YOUR_CLOUDFLARE_SECRET_KEY_HERE"

client = AsyncIOMotorClient(MONGO_URI)
db = client["bypass_protector"]
links_col = db["links"]

@app.get("/visit", response_class=HTMLResponse)
async def visit_page(request: Request, id: str):
    # Check karna ki yeh ID database me hai ya nahi
    link_data = await links_col.find_one({"_id": id})
    if not link_data:
        raise HTTPException(status_code=404, detail="Link invalid ya expire ho chuka hai.")
    
    # User ko html page dena ID ke sath
    return templates.TemplateResponse("index.html", {"request": request, "link_id": id})

@app.post("/redirect")
async def handle_redirect(link_id: str = Form(...), captcha_response: str = Form(None, alias="cf-turnstile-response")):
    # 1. Cloudflare Captcha Verification (Bypass scripts ko rokne ke liye sabse zaroori step)
    if not captcha_response:
        raise HTTPException(status_code=400, detail="Captcha verification required!")
        
    verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    payload = {
        "secret": CLOUDFLARE_SECRET_KEY,
        "response": captcha_response
    }
    
    response = requests.post(verify_url, data=payload).json()
    
    if not response.get("success"):
        raise HTTPException(status_code=403, detail="Captcha verification failed. Automation blocked!")

    # 2. Agar verification pass ho gayi, toh database se original link nikalna
    link_data = await links_col.find_one({"_id": link_id})
    if not link_data:
        raise HTTPException(status_code=404, detail="Link data not found.")
    
    # 3. Anti-Bypass Rule: Ek baar link use hone ke baad use delete kar do taaki koi use reuse na kar paye
    await links_col.delete_one({"_id": link_id})
    
    # 4. Final Redirect
    return RedirectResponse(url=link_data["original_url"], status_code=303)
