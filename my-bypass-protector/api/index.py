from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# ⚠️ Apna asli MongoDB link yahan zaroor daalna bhai
MONGO_URI = "mongodb+srv://gxmon239:f4l7bKrhka3Fh2cV@cluster0.qmblwql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client["bypass_protector"]
links_col = db["links"]

def get_html_page(link_id: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Link Verification</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .container {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 100%; }}
            h2 {{ color: #333; margin-bottom: 10px; }}
            p {{ color: #666; font-size: 14px; margin-bottom: 25px; }}
            .timer-text {{ font-size: 18px; font-weight: bold; color: #ff4757; margin-bottom: 20px; }}
            .btn {{ background-color: #007bff; color: white; border: none; padding: 12px 25px; font-size: 16px; border-radius: 6px; cursor: pointer; width: 100%; transition: 0.3s; font-weight: bold; }}
            .btn:disabled {{ background-color: #cccccc; cursor: not-allowed; }}
            .btn:hover:enabled {{ background-color: #0056b3; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h2>🔒 Security Verification</h2>
        <p>Bypass protection is active. Please wait for the timer to complete.</p>
        <div class="timer-text" id="timer_display">Please wait 5 seconds...</div>
        <form action="/redirect" method="POST">
            <input type="hidden" name="link_id" value="{link_id}">
            <button type="submit" class="btn" id="submit_btn" disabled>Verify & Continue</button>
        </form>
    </div>
    <script>
        let timeLeft = 5; 
        const timerDisplay = document.getElementById('timer_display');
        const submitBtn = document.getElementById('submit_btn');
        const countdown = setInterval(() => {{
            timeLeft--;
            if (timeLeft <= 0) {{
                clearInterval(countdown);
                timerDisplay.innerHTML = "✅ Verification Ready!";
                timerDisplay.style.color = "#2ed573";
                submitBtn.disabled = false;
            }} else {{
                timerDisplay.innerHTML = `Please wait ${{timeLeft}} seconds...`;
            }}
        }}, 1000);
    </script>
    </body>
    </html>
    """

@app.get("/")
async def home():
    return {"status": "Server is running smoothly without errors!"}

@app.get("/visit", response_class=HTMLResponse)
async def visit_page(id: str):
    link_data = await links_col.find_one({"_id": id})
    if not link_data:
        return HTMLResponse(content="<h2>⚠️ Link Expired ya Invalid hai!</h2>", status_code=404)
    return HTMLResponse(content=get_html_page(id))

@app.post("/redirect")
async def handle_redirect(link_id: str = Form(...)):
    link_data = await links_col.find_one({"_id": link_id})
    if not link_data:
        raise HTTPException(status_code=404, detail="Session Expired")
    
    await links_col.delete_one({"_id": link_id})
    return RedirectResponse(url=link_data["original_url"], status_code=303)
