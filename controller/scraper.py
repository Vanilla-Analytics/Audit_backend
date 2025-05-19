#scraper.py
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse

async def extract_brand_name(page):
    try:
        # Priority 1: Meta tag
        brand = await page.evaluate("""
            () => {
                const meta = document.querySelector('meta[property="og:site_name"], meta[name="application-name"]');
                return meta ? meta.getAttribute('content') : null;
            }
        """)
        if brand:
            return brand.strip()

        # Priority 2: Title tag
        title = await page.title()
        if title:
            for sep in ["|", "-", "»", ":"]:
                if sep in title:
                    return title.split(sep)[0].strip()
            return title.strip()

        # Priority 3: Logo alt or filename
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

        # Priority 4: Footer text
        brand = await page.evaluate("""
            () => {
                const footer = document.querySelector('footer');
                if (footer) {
                    const text = footer.innerText;
                    const match = text.match(/©\\s*(.*?)\\s*\\d{4}/);
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
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        brand_name = None
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            content = await page.evaluate("""() => {
                const text = document.body.innerText || '';
                return text.length < 200 ? document.documentElement.innerHTML : text;
            }""")
            brand_name = await extract_brand_name(page)
        except Exception as e:
            content = f"Error loading page: {str(e)}"
        finally:
            await browser.close()

        return content, brand_name
