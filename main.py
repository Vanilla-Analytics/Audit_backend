import asyncio
import sys

print("✅ Python version in use:", sys.version)

if sys.platform.startswith("win"):
    print("✅ Setting WindowsSelectorEventLoopPolicy")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Request
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import JSONResponse
from controller.web_scrapping import process_website
from controller.to_pdf import generate_pdf
from supabase import create_client
import os
import uuid
import logging

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

#BASE_URL = os.getenv("BASE_URL")
#if not BASE_URL:
    #raise RuntimeError("❌ BASE_URL not set in environment")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


# Create FastAPI instance
app = FastAPI()

# CORS configuration - use FastAPI's middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Supabase config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Add OPTIONS handler for CORS preflight requests
@app.options("/submit")
async def options_submit():
    return JSONResponse(
        status_code=200,
        content={"message": "OK"}
    )

@app.post("/submit")
async def handle_form(request: Request):
    try:
        data = await request.json()
        name = data.get("name") 
        print(name)
        email = data.get("email")
        print(email)
        url = data.get("url")
        print(url)
        return JSONResponse(
            status_code=200,
            content={"message": "Form submitted successfully"}
        )
        logger.info(f"Processing submission for {name}, {email}, URL: {url}")
        session_id = str(uuid.uuid4())
        output_dir = f"outputs/{session_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Process the URL and generate content
        content_data = await process_website(url, output_dir)
        
        # Generate PDF
        pdf_path = generate_pdf(content_data, output_dir, session_id)
        
        # Store user info in Supabase
        supabase.table("user_requests").insert({
            "name": name,
            "email": email,
            "url": url
        }).execute()
                
        #pdf_url = f"{BASE_URL}/{pdf_path}"
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

# For debugging/testing purposes
#if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run(app, host="0.0.0.0")