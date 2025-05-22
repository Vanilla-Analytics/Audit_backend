import asyncio
import sys
import json
import os
import uuid
import logging
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from controller.web_scrapping import process_website
from controller.to_pdf import generate_pdf
from supabase import create_client

print("✅ Python version in use:", sys.version)
if sys.platform.startswith("win"):
    print("✅ Setting WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FRONTEND_URL = os.getenv("FRONTEND_URL", "*").strip()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Progress tracker store
progress_tracker = {}

@app.middleware("http")
async def log_origin(request: Request, call_next):
    print("🔍 Origin Header:", request.headers.get("origin"))
    return await call_next(request)

@app.get("/progress/{session_id}")
async def progress_stream(session_id: str):
    async def event_generator() -> AsyncGenerator[str, None]:
        last_progress = None
        while True:
            progress = progress_tracker.get(session_id)
            if progress and progress != last_progress:
                yield f"data: {json.dumps(progress)}\n\n"
                last_progress = progress
                if progress.get("percent", 0) >= 100:
                    break
            await asyncio.sleep(0.3)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

def upload_pdf_to_supabase(pdf_path: str, session_id: str) -> str:
    try:
        with open(pdf_path, "rb") as f:
            content = f.read()
        file_path = f"{session_id}.pdf"
        bucket = supabase.storage.from_("pdfs")
        response = bucket.upload(
            file_path,
            content,
            {
                "content-type": "application/pdf",
                "x-upsert": "true"
            }
        )
        logger.info(f"Supabase upload response: {response}")
        if not response or not hasattr(response, 'path'):
            raise RuntimeError("Upload failed: Invalid response from Supabase")
        public_url = bucket.get_public_url(response.path)
        logger.info(f"Public URL: {public_url}")
        return public_url
    except Exception as e:
        logger.error(f"Failed to upload PDF to Supabase: {str(e)}", exc_info=True)
        raise RuntimeError("Failed to upload PDF to storage")

@app.post("/submit")
async def handle_form(request: Request):
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        url = data.get("url")
        session_id = data.get("session_id", str(uuid.uuid4()))

        logger.info(f"Processing submission for {name}, {email}, URL: {url}")
        output_dir = f"outputs/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        content_data = await process_website(url, output_dir, session_id=session_id)
        pdf_path = generate_pdf(content_data, output_dir, session_id)

        supabase.table("user_requests").insert({
            "name": name,
            "email": email,
            "url": url
        }).execute()

        pdf_url = upload_pdf_to_supabase(pdf_path, session_id)
        logger.info(f"PDF generated successfully: {pdf_url}")

        return {"pdf_url": pdf_url}
    except Exception as e:
        logger.error(f"Error processing submission: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to process request: {str(e)}"}
        )

@app.get("/")
def route():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=int(os.environ["PORT"])  # <- Uses Railway's dynamic port
    )


# For debugging/testing purposes
#if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run(app, host="0.0.0.0")