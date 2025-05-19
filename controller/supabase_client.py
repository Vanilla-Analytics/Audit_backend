from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_summary_to_supabase(url, summary_json):
    response = supabase.table("web_summaries").insert({
        "url": url,
        "Summary": summary_json
    }).execute()
    return response.data

