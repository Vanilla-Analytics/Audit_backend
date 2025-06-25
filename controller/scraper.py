#scraper.py

import asyncio
from playwright.async_api import async_playwright
#from playwright_stealth import add_stealth
from playwright_stealth import stealth_async
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import os
import requests


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
    except Exception as e:
        print("Brand extraction error:", str(e))
    return None


async def scrape_page_content(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            locale="en-US",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await stealth_async(page)
        #await add_stealth(page)

        content = ""
        brand_name = None

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=80000)
            await asyncio.sleep(3)

            # Get all visible text except script/style/svg/canvas
            content = await page.evaluate("""
                () => {
                    const ignore = ['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG', 'CANVAS'];

                    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
                    let textContent = '';
                    
                    while (walker.nextNode()) {
                        const node = walker.currentNode;
                        const parentTag = node.parentNode?.nodeName?.toUpperCase();
                        if (parentTag && !ignore.includes(parentTag) && node.nodeValue.trim().length > 10)  {
                            textContent += node.nodeValue.trim() + '\\n';
                        }
                    }
                    return textContent;
                }
            """)

            # Fallback to meta description
            if len(content.strip().split()) < 30:
                print("⚠️ Content too short — trying meta description fallback")
                title = await page.title()
                description = await page.evaluate("""
                    () => {
                        const desc = document.querySelector('meta[name="description"]');
                        return desc ? desc.content : '';
                    }
                """)
                content = (description or title or '') + "\n\n" + content

            if not content or len(content.strip().split()) < 30:
                raise ValueError("Scraping failed: insufficient meaningful content extracted.")

            brand_name = await extract_brand_name(page)

        except Exception as e:
            print("❌ Error during scraping:", str(e))
            raise ValueError("Website scraping failed: " + str(e))

        finally:
            await browser.close()

        return content.strip(), brand_name
