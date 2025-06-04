#scraper.py
# Final scraper.py: JS-heavy + Lazy-load + OCR fallback
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import os


def jina_reader_extract(url: str) -> str:
    try:
        response = requests.post("https://reader.jina.ai/api/v1/read", json={"url": url})
        response.raise_for_status()
        return response.json().get("text", "")
    except Exception as e:
        print("⚠️ Jina Reader Error:", str(e))
        return ""

async def extract_brand_name(page):
    try:
        brand = await page.evaluate("""
            () => {
                const meta = document.querySelector('meta[property="og:site_name"], meta[name="application-name"]');
                return meta ? meta.getAttribute('content') : null;
            }
        """)
        if brand:
            return brand.strip()

        title = await page.title()
        if title:
            for sep in ["|", "-", ":"]:
                if sep in title:
                    return title.split(sep)[0].strip()
            return title.strip()

        brand = await page.evaluate("""
            () => {
                const logo = document.querySelector('img[alt*="logo"], img[src*="logo"]');
                if (logo?.alt) return logo.alt;
                if (logo?.src) {
                    const src = logo.src.split('/').pop().split('.')[0];
                    return src.replace(/[^a-zA-Z ]/g, ' ').trim();
                }
                return null;
            }
        """)
        if brand:
            return brand.strip()

        brand = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer');
                if (footer) {
                    const text = footer.innerText;
                    const match = text.match(/\u00a9\s*(.*?)\s*\d{4}/);
                    return match ? match[1] : null;
                }
                return null;
            }
        """)
        if brand:
            return brand.strip()

    except Exception as e:
        print("Brand extraction error:", str(e))

    return None

async def scrape_page_content(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await stealth_async(page)

        brand_name = None
        content = ""
        ocr_path = "/tmp/screenshot.png" if os.name != "nt" else "screenshot.png"

        try:
            await page.goto(url, wait_until="networkidle", timeout=90000)
            await page.wait_for_selector("body", timeout=15000)

            # Scroll to trigger lazy-loading
            await page.evaluate("""
                () => {
                    return new Promise((resolve) => {
                        let totalHeight = 0;
                        const distance = 100;
                        const timer = setInterval(() => {
                            window.scrollBy(0, distance);
                            totalHeight += distance;
                            if (totalHeight >= document.body.scrollHeight) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 100);
                    });
                }
            """)
            await asyncio.sleep(4)

            # Try innerText first
            content = await page.evaluate("() => document.body.innerText")

            # Fallback to HTML
            if not content or len(content.strip()) < 200:
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                content = soup.get_text(separator=" ", strip=True)

            block_keywords = ["captcha", "verify you are human", "access denied", "unusual traffic", "blocked"]
            if not content or len(content.strip()) < 200 or any(k in content.lower() for k in block_keywords):
                print("🛡️ Weak content — OCR fallback triggered")
                await page.screenshot(path=ocr_path, full_page=True)
                content = pytesseract.image_to_string(Image.open(ocr_path))

            # If OCR also fails, try Jina reader
            if not content or len(content.strip()) < 200:
                print("🧪 OCR failed — using Jina Reader as last resort")
                content = jina_reader_extract(url)

            brand_name = await extract_brand_name(page)

        except Exception as e:
            print("❌ Error during scraping:", str(e))
            content = f"Error loading page: {str(e)}"

        finally:
            await browser.close()

        return content.strip(), brand_name


#--------------------------------------------------------------------------------------------------
# import asyncio
# from playwright.async_api import async_playwright 
# from urllib.parse import urlparse

# import requests

# def jina_reader_extract(url: str) -> str:
#     try:
#         response = requests.post("https://reader.jina.ai/api/v1/read", json={"url": url})
#         response.raise_for_status()
#         return response.json().get("text", "")
#     except Exception as e:
#         print("⚠️ Jina Reader Error:", str(e))
#         return ""


# async def extract_brand_name(page):
#     try:
#         # Priority 1: Meta tag
#         brand = await page.evaluate("""
#             () => {
#                 const meta = document.querySelector('meta[property="og:site_name"], meta[name="application-name"]');
#                 return meta ? meta.getAttribute('content') : null;
#             }
#         """)
#         if brand:
#             return brand.strip()

#         # Priority 2: Title tag
#         title = await page.title()
#         if title:
#             for sep in ["|", "-", "»", ":"]:
#                 if sep in title:
#                     return title.split(sep)[0].strip()
#             return title.strip()

#         # Priority 3: Logo alt or filename
#         brand = await page.evaluate("""
#             () => {
#                 const logo = document.querySelector('img[alt*="logo"], img[src*="logo"]');
#                 if (logo?.alt) return logo.alt;
#                 if (logo?.src) {
#                     const src = logo.src.split('/').pop().split('.')[0];
#                     return src.replace(/[^a-zA-Z ]/g, ' ').trim();
#                 }
#                 return null;
#             }
#         """)
#         if brand:
#             return brand.strip()

#         # Priority 4: Footer text
#         brand = await page.evaluate("""
#             () => {
#                 const footer = document.querySelector('footer');
#                 if (footer) {
#                     const text = footer.innerText;
#                     const match = text.match(/©\\s*(.*?)\\s*\\d{4}/);
#                     return match ? match[1] : null;
#                 }
#                 return null;
#             }
#         """)
#         if brand:
#             return brand.strip()

#     except Exception as e:
#         print("Brand extraction error:", str(e))

#     return None



# async def scrape_page_content(url):
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=True)
#         page = await browser.new_page()
#         brand_name = None
#         content = ""

#         try:
#             await page.goto(url, wait_until="domcontentloaded", timeout=60000)
#             await page.wait_for_load_state("networkidle")
#             await asyncio.sleep(2)  # Allow dynamic JS content to render

#             # Attempt innerText extraction
#             content = await page.evaluate("""() => {
#                 return document.body.innerText || '';
#             }""")

#             # --- Step 1: Check for bot protection / CAPTCHA ---
#             block_keywords = [
#                 "captcha", "verify you are human", "access denied",
#                 "unusual traffic", "blocked", "security check"
#             ]

#             if (
#                 not content or
#                 len(content.strip()) < 200 or
#                 any(keyword in content.lower() for keyword in block_keywords)
#             ):
#                 print(" Bot protection or weak content detected — using Jina Reader fallback")
#                 content = jina_reader_extract(url)

#             # --- Step 2: Extract brand name if not blocked ---
#             brand_name = await extract_brand_name(page)

#         except Exception as e:
#             print(" Error during scraping:", str(e))
#             content = f"Error loading page: {str(e)}"

#         finally:
#             await browser.close()

#         return content.strip(), brand_name  

