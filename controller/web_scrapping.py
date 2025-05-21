#main.py
import asyncio
from controller.scraper import scrape_page_content
from controller.ai_processor import generate_response
from controller.save_results import save_to_json
from controller.to_pdf import generate_pdf

# Ensure generate_pdf is used correctly
save_to_pdf = generate_pdf  # Assuming save_to_pdf is intended to call generate_pdf
from controller.prompts import SOP_PROMPTS, BRANDING_INTRO
from controller.supabase_client import upload_summary_to_supabase

import re

def fallback_brand_name(url):
    from urllib.parse import urlparse
    hostname = urlparse(url).hostname or ''
    hostname = hostname.replace('www.', '')
    domain = hostname.split('.')[0]  # 'homedone'

    # Insert spaces before capital letters or when letters switch from lower to upper
    # And also split compound words like 'homedone' → ['home', 'done']
    spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', domain)  # handle camelCase
    spaced = re.sub(r'[^a-zA-Z]', ' ', spaced)  # remove numbers/symbols
    spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', spaced)  # snake_case
    # Try inserting space in the middle (for words like homedone)
    parts = re.findall('[a-zA-Z][^A-Z]*', domain)
    brand_guess = ' '.join(part.capitalize() for part in parts if len(part) > 1)

    return brand_guess or domain.capitalize()


def is_valid_brand_name(name):
    if not name or len(name) < 2:
        return False
    generic_terms = {"home", "page", "site", "index", "default", "smith", "furniture", "co", "uk"}
    name_lower = name.lower()
    return (
        all(term not in name_lower for term in generic_terms)
        and '.' not in name_lower  # avoid things like 'homedone.co.uk'
    )


async def main(url):
    print("🔍 Scraping content...")
    page_text, detected_brand = await scrape_page_content(url)


    detected_brand = (detected_brand or '').replace('\n', '').replace('"', '').strip()
    if '.' in detected_brand or not is_valid_brand_name(detected_brand):
        brand_name = fallback_brand_name(url)
    else:
        brand_name = detected_brand
    brand_name = detected_brand if is_valid_brand_name(detected_brand) else fallback_brand_name(url)

    print(f"🧠 Final Brand Name: {brand_name}\nGenerating Website Description...")

    chat_history = []

    description_prompt = (
        "In a short paragraph, summarize what this website is about based on its content. "
        "Focus on the business, products/services offered, and the tone."
        f"\n\nPage Content:\n{page_text}"
    )

    try:
        website_description, chat_history = generate_response(chat_history, description_prompt, brand_name)
    except Exception as e:
        print("⚠️ Failed to generate website description:", str(e))
        website_description = "This is a business website."

    print("🧠 Generating AI responses based on Website Description...")
    responses = {}

    for key, sop_prompt in SOP_PROMPTS.items():
        print(f"→ {key}")
        full_prompt = f"{sop_prompt}\n\nWebsite Description:\n{website_description}"
        try:
            response, chat_history = generate_response(chat_history, full_prompt, brand_name)
            if key == "branding_messaging":
                response = BRANDING_INTRO.format(brand_name=brand_name) + "\n\n" + response
                
            responses[key] = response
        except Exception as e:
            responses[key] = f"Error generating response: {str(e)}"

    responses['brand_name'] = brand_name

    print("💾 Saving JSON locally...")
    save_to_json(responses)

    print("☁️ Uploading JSON to Supabase...")
    upload_summary_to_supabase(url, responses)

    print("📝 Generating PDF...")
    save_to_pdf(responses)

    print("✅ Done! You can now download your PDF.")

async def process_website(url, output_dir):
    from pathlib import Path

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    async def runner():
        print("🔍 Scraping content...")
        page_text, detected_brand = await scrape_page_content(url)

        detected_brand = (detected_brand or '').replace('\n', '').replace('"', '').strip()
        if '.' in detected_brand or not is_valid_brand_name(detected_brand):
            brand_name = fallback_brand_name(url)
        else:
            brand_name = detected_brand
        brand_name = detected_brand if is_valid_brand_name(detected_brand) else fallback_brand_name(url)

        chat_history = []

        description_prompt = (
            "In a short paragraph, summarize what this website is about based on its content. "
            "Focus on the business, products/services offered, and the tone."
            f"\n\nPage Content:\n{page_text}"
        )

        try:
            website_description, chat_history = generate_response(chat_history, description_prompt, brand_name)
        except Exception as e:
            website_description = "This is a business website."
        
        STRUCTURED_KEYS = {
            "swot_analysis",
            "porter_analysis",
            "copy_gap_analysis",
            "copy_suggestions",
            "recommendations"
        }
        responses = {}
        for key, sop_prompt in SOP_PROMPTS.items():
            print(f"→ {key}") 
            full_prompt = f"{sop_prompt}\n\nWebsite Description:\n{website_description}"
            try:
                temperature = 0.0 if key in STRUCTURED_KEYS else 0.7  
                response, chat_history = generate_response(chat_history, full_prompt, brand_name,temperature=temperature)
                if key == "branding_messaging":
                    response = BRANDING_INTRO.format(brand_name=brand_name) + "\n\n" + response
                responses[key] = response
            except Exception as e:
                responses[key] = f"Error generating response: {str(e)}"

        responses['brand_name'] = brand_name

        # Save JSON and PDF
        save_to_json(responses, output_dir)
        upload_summary_to_supabase(url, responses)
        return responses

    return await runner()  # Just await the coroutine directly

if __name__ == "__main__":
    url = input("Enter website URL: ").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    asyncio.run(main(url))
