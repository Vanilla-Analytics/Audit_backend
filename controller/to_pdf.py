from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Frame, Spacer, KeepInFrame
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

import os
import re
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#FONT_PATH = os.path.join(BASE_DIR,"..", "assets", "Aerial.ttf")
#pdfmetrics.registerFont(TTFont("Anton", os.path.join(BASE_DIR,"Anton.ttf")))
#pdfmetrics.registerFont(TTFont("Aerial","..", "assets", FONT_PATH))
#-------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ANTON_FONT_PATH = os.path.join(BASE_DIR, "..", "assets", "fonts", "Anton.ttf")
AERIAL_FONT_PATH = os.path.join(BASE_DIR, "..", "assets", "fonts", "Aerial.ttf")

# Register fonts properly
pdfmetrics.registerFont(TTFont("Anton", ANTON_FONT_PATH))
pdfmetrics.registerFont(TTFont("Aerial", AERIAL_FONT_PATH))

#------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#Layout
PAGE_WIDTH = 1000
PAGE_HEIGHT = 600
LEFT_MARGIN = inch
RIGHT_MARGIN = inch
TOP_MARGIN = 1.2 * inch
BOTTOM_MARGIN = inch

LOGO_WIDTH = 240
LOGO_HEIGHT = 45
LOGO_Y_OFFSET = PAGE_HEIGHT - TOP_MARGIN + 10
#LOGO_PATH = os.path.join(BASE_DIR, "Data_Vinci_Logo.png")
LOGO_PATH = os.path.join(BASE_DIR, "..", "assets", "Data_Vinci_logo.png")

def sanitize_text(text):
    if not isinstance(text, str):
        text = str(text)
    text = text.replace('*', '').replace('✔', '').replace('✖', '').replace('🔹', '').replace('⚠', '').replace('®','')
    text = text.replace('—', '-').replace('–', '-').replace('“', '"').replace('”', '"').replace('’', "'")
    return text.strip()


def generate_pdf(responses, output_dir, session_id):
    file_path = os.path.join(output_dir, f"report_{session_id}.pdf")
    c = canvas.Canvas(file_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    
    def draw_heading_on_left(title_key):
   
        safe_key = title_key.upper().replace(" ", "_").replace("&", "").replace("'", "").replace("-", "")
        image_name = f"heading_{safe_key}.png"
        image_path = os.path.join(BASE_DIR, "..", "assets", image_name)

    # Calculate left section width (40% of page width)
        left_section_width = PAGE_WIDTH * 0.4

    # Set desired image size (adjust if needed)
        image_width = left_section_width * 0.8     # 80% of left section width
        image_height = 300  # adjust height if needed

    # Calculate x and y positions to center the image in the left section
        x = (left_section_width - image_width) / 2
        y = (PAGE_HEIGHT - image_height) / 2

        if os.path.exists(image_path):
            c.drawImage(image_path, x, y, width=image_width, height=image_height, mask='auto')
        else:
            print(f"[!] Heading image not found: {image_path}")

    def draw_header():
        

        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

    # Pink horizontal line directly after logo
        line_start = LEFT_MARGIN + LOGO_WIDTH + 10
        line_y = logo_y + LOGO_HEIGHT / 2 
        c.setStrokeColor(colors.HexColor("#ef1fb3"))
        c.setLineWidth(4)
        c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)

    def draw_footer_cta():
        sticker_text = "CLAIM YOUR FREE\nSTRATEGY SESSION"
        link_url = "https://datavinci.services/certified-google-analytics-consultants/?utm_source=ga4_audit&utm_medium=looker_report"

    # Coordinates for bottom-right
        sticker_x = PAGE_WIDTH - 250
        sticker_y = 25
        sticker_width = 180
        sticker_height = 40

    # Sticker rectangle
        c.setFillColor(colors.HexColor("#007FFF"))
        c.roundRect(sticker_x, sticker_y, sticker_width, sticker_height, 8, stroke=0, fill=1)

    # Text inside sticker
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(sticker_x + sticker_width / 2, sticker_y + 24, "CLAIM YOUR FREE")
        c.drawCentredString(sticker_x + sticker_width / 2, sticker_y + 12, "STRATEGY SESSION")

    #clickable
        c.linkURL(link_url, (sticker_x, sticker_y, sticker_x + sticker_width, sticker_y + sticker_height), relative=0)
    
    

    def draw_intro_page(brand_name, branding_llm_content):
        #c.showPage()

    # Header: Logo + Title
        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

    # Pink horizontal line directly after logo
        line_start = LEFT_MARGIN + LOGO_WIDTH + 10
        line_y = logo_y + LOGO_HEIGHT / 2 
        c.setStrokeColor(colors.HexColor("#ef1fb3"))
        c.setLineWidth(4)
        c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)


    # Pink sticker
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # Heading
        heading_font = "Anton"
        heading_size = 55
        heading_text = "BRANDING & MESSAGING"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)
        #heading_y = draw_heading_image("BRANDING_MESSAGING")

        #Blue line with space below heading

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        underline_y = heading_y - 20  # ← spacing between heading and line

        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, underline_y, LEFT_MARGIN + heading_width, underline_y)


    # Paragraph (adjusted lower to avoid overlapping)
        #fixed_intro = f"""This audit identifies missed revenue opportunities in {brand_name}'s marketing funnel by analyzing gaps between its proven product advantages and current messaging effectiveness. We evaluate how unclear copy, underutilized social proof, and inconsistent brand positioning."""
        fixed_intro = ""
        llm_content = sanitize_text(branding_llm_content)
        content_style = ParagraphStyle(
            'intro_paragraph',
            fontName='Helvetica',
            fontSize=15,
            leading=18,
            textColor=colors.black,
            alignment=0
        )
    
        frame_top_y = heading_y - 50  # 40pt space after heading + blue line
        frame_height = 3.5 * inch
        frame = Frame(LEFT_MARGIN, frame_top_y - frame_height, PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN, frame_height, showBoundary=0)
        story = [
            Paragraph(fixed_intro, content_style),
            Spacer(1, 12),
            Paragraph(llm_content, content_style)
        ]
        frame.addFromList(story, c)

        draw_footer_cta()
    
    def Brand_Analysis_page():
        c.showPage()

    # --- Header: Logo + Pink Line ---
        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

            line_start = LEFT_MARGIN + LOGO_WIDTH + 10
            line_y = logo_y + LOGO_HEIGHT / 2
            c.setStrokeColor(colors.HexColor("#ef1fb3"))
            c.setLineWidth(4)
            c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)

    # --- Pink Sticker ---
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # --- Heading ---
        heading_font = "Anton"
        heading_size = 50
        heading_text = "BRAND ANALYSIS"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, heading_y - 20, LEFT_MARGIN + heading_width, heading_y - 20)

    # --- Replace single image with 3 icon images with text beside them in 2 lines ---
        icon_paths = [
            os.path.join(BASE_DIR,  "..", "assets","brand_visuals_icon.png"),
            os.path.join(BASE_DIR, "..", "assets", "brand_personality_icon.png"),
            os.path.join(BASE_DIR, "..", "assets", "brand_positioning_icon.png")
        ]
    
    # Text in two parts: [first line, second line]
        icon_texts = [
            ["BRAND", "VISUALS"], 
            ["BRAND", "PERSONALITY"], 
            ["BRAND", "POSITIONING"]
        ]
    
    # Set up dimensions
        icon_size = 80  # Size of each circular icon
        total_width = PAGE_WIDTH - (2 * LEFT_MARGIN)  # Available width
    
    # Starting Y position below the blue line
        icon_top_y = heading_y - 120
        icon_center_y = icon_top_y  # Center point of the icon
    
    # Draw each icon with text beside it
        for i in range(3):
        # Calculate starting position for each group
            if i == 0:
                x_pos = LEFT_MARGIN
            else:
                x_pos = LEFT_MARGIN + (i * 280)  # Evenly space the three groups
        
        # Draw circle with lime green background for icon
            c.setFillColor(colors.HexColor("#c5ff54"))  # Lime green color from the image
            c.circle(x_pos + (icon_size/2), icon_center_y, icon_size/2, fill=1, stroke=0)  # No stroke
        
        # Try to draw icon image
            if os.path.exists(icon_paths[i]):
                c.drawImage(icon_paths[i], x_pos, icon_center_y - (icon_size/2), width=icon_size, height=icon_size, mask='auto')
            else:
                print(f"[!] Icon image not found: {icon_paths[i]}")
        
        # Draw text beside icon using same font as heading
            c.setFont(heading_font, 30)  # Size for the icon labels
            c.setFillColor(colors.HexColor("#424242"))  # Same color as heading
        
        # Position text to the right of the icon
            text_x = x_pos + icon_size + 15  # Spacing between icon and text
        
        # Calculate heights for better vertical centering
            line_height = 35 # Height for each line of text
            text_height_total = 60  # Total height for both lines
            line_gap = 12 # Gap between lines
            
            vertical_adjustment = -18
        
            first_line_y = icon_center_y + (line_height + line_gap)/2 + vertical_adjustment # First line position
            second_line_y = icon_center_y - (line_height - line_gap)/2 + vertical_adjustment # Second line position
        
        # Draw first line (BRAND)
            c.drawString(text_x, first_line_y, icon_texts[i][0])
        
        # Draw second line (VISUALS/PERSONALITY/POSITIONING)
            c.drawString(text_x, second_line_y, icon_texts[i][1])
    
        draw_footer_cta()

    def Copy_Gap_Analysis_Page(content):
        c.showPage()
        draw_header()

    # Heading
        heading = "COPY GAP ANALYSIS"
        heading_font = "Anton"
        heading_size = 42
        heading_y = PAGE_HEIGHT - 3 * inch
        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading)

        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(6)
        heading_width = c.stringWidth(heading, heading_font, heading_size)
        c.line(LEFT_MARGIN, heading_y - 15, LEFT_MARGIN + heading_width, heading_y - 15)

    # Body text setup
        body_y = heading_y - 60
        body_font = "Helvetica"
        body_size = 13
        line_spacing = 22
        max_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
        c.setFont(body_font, body_size)
        c.setFillColor(colors.HexColor("#424242"))

    # Clean and parse each line
        lines = content.strip().split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        for line in lines:
            if body_y < 100:
                break
            c.drawString(LEFT_MARGIN, body_y, line)
            body_y -= line_spacing

        draw_footer_cta()

    def Business_Model_Analysis_page():
        c.showPage()

    # --- Header: Logo + Pink Line ---
        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

            line_start = LEFT_MARGIN + LOGO_WIDTH + 10
            line_y = logo_y + LOGO_HEIGHT / 2
            c.setStrokeColor(colors.HexColor("#ef1fb3"))
            c.setLineWidth(4)
            c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)

    # --- Pink Sticker ---
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # --- Heading ---
        heading_font = "Anton"
        heading_size = 50
        heading_text = "BUSINESS MODEL ANALYSIS"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, heading_y - 20, LEFT_MARGIN + heading_width, heading_y - 20)

    # --- Replace single image with 3 icon images with text beside them in 2 lines ---
        icon_paths = [
            os.path.join(BASE_DIR, "..", "assets","business_description_icon.png"),
            os.path.join(BASE_DIR,"..", "assets", "revenue_model_icon.png"),
            os.path.join(BASE_DIR,"..", "assets", "target_audience_icon.png"),
            os.path.join(BASE_DIR, "..", "assets","business_analysis_icon.png")
        ]
    
    # Text in two parts: [first line, second line]
        icon_texts = [
            ["BUSINESS", "DESCRIPTION"], 
            ["REVENUE", "MODEL"], 
            ["TARGET", "AUDIENCE"],
            ["BUSINESS", "ANALYSIS"]
        ]
    
    # Set up dimensions
        icon_size = 60  # Size of each circular icon
        total_width = PAGE_WIDTH - (2 * LEFT_MARGIN)  # Available width
    
    # Starting Y position below the blue line
        icon_top_y = heading_y - 120
        icon_center_y = icon_top_y  # Center point of the icon
    
    # Draw each icon with text beside it
        for i in range(4):
        # Calculate starting position for each group
            if i == 0:
                x_pos = LEFT_MARGIN
            else:
                x_pos = LEFT_MARGIN + (i * 220)  # Evenly space the three groups
        
        # Draw circle with lime green background for icon
            c.setFillColor(colors.HexColor("#c5ff54"))  # Lime green color from the image
            c.circle(x_pos + (icon_size/2), icon_center_y, icon_size/2, fill=1, stroke=0)  # No stroke
        
        # Try to draw icon image
            if os.path.exists(icon_paths[i]):
                c.drawImage(icon_paths[i], x_pos, icon_center_y - (icon_size/2), width=icon_size, height=icon_size, mask='auto')
            else:
                print(f"[!] Icon image not found: {icon_paths[i]}")
        
        # Draw text beside icon using same font as heading
            c.setFont(heading_font, 26)  # Size for the icon labels
            c.setFillColor(colors.HexColor("#424242"))  # Same color as heading
        
        # Position text to the right of the icon
            text_x = x_pos + icon_size + 15  # Spacing between icon and text
        
        # Calculate heights for better vertical centering
            line_height = 35 # Height for each line of text
            text_height_total = 60  # Total height for both lines
            line_gap = 12 # Gap between lines
            
            vertical_adjustment = -18
        
            first_line_y = icon_center_y + (line_height + line_gap)/2 + vertical_adjustment # First line position
            second_line_y = icon_center_y - (line_height - line_gap)/2 + vertical_adjustment # Second line position
        
        # Draw first line (BRAND)
            c.drawString(text_x, first_line_y, icon_texts[i][0])
        
        # Draw second line (VISUALS/PERSONALITY/POSITIONING)
            c.drawString(text_x, second_line_y, icon_texts[i][1])
    
        draw_footer_cta()

    def Copy_Analysis_page():
        c.showPage()

    # --- Header: Logo + Pink Line ---
        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

            line_start = LEFT_MARGIN + LOGO_WIDTH + 10
            line_y = logo_y + LOGO_HEIGHT / 2
            c.setStrokeColor(colors.HexColor("#ef1fb3"))
            c.setLineWidth(4)
            c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)

    # --- Pink Sticker ---
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # --- Heading ---
        heading_font = "Anton"
        heading_size = 50
        heading_text = "COPY ANALYSIS"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, heading_y - 20, LEFT_MARGIN + heading_width, heading_y - 20)

    # --- Replace single image with 3 icon images with text beside them in 2 lines ---
        icon_paths = [
            os.path.join(BASE_DIR,"..", "assets", "ideal_copy_style_icon.png"),
            os.path.join(BASE_DIR, "..", "assets","copy_gap_analysis_icon.png"),
            os.path.join(BASE_DIR,"..", "assets", "copy_suggestion_icon.png")
        ]
    
    # Text in two parts: [first line, second line]
        icon_texts = [
            ["IDEAL", "COPY STYLE"], 
            ["COPY GAP", "ANALYSIS"], 
            ["COPY", "SUGGESTION"]
        ]
    
    # Set up dimensions
        icon_size = 80  # Size of each circular icon
        total_width = PAGE_WIDTH - (2 * LEFT_MARGIN)  # Available width
    
    # Starting Y position below the blue line
        icon_top_y = heading_y - 120
        icon_center_y = icon_top_y  # Center point of the icon
    
    # Draw each icon with text beside it
        for i in range(3):
        # Calculate starting position for each group
            if i == 0:
                x_pos = LEFT_MARGIN
            else:
                x_pos = LEFT_MARGIN + (i * 280)  # Evenly space the three groups
        
        # Draw circle with lime green background for icon
            c.setFillColor(colors.HexColor("#c5ff54"))  # Lime green color from the image
            c.circle(x_pos + (icon_size/2), icon_center_y, icon_size/2, fill=1, stroke=0)  # No stroke
        
        # Try to draw icon image
            if os.path.exists(icon_paths[i]):
                c.drawImage(icon_paths[i], x_pos, icon_center_y - (icon_size/2), width=icon_size, height=icon_size, mask='auto')
            else:
                print(f"[!] Icon image not found: {icon_paths[i]}")
        
        # Draw text beside icon using same font as heading
            c.setFont(heading_font, 30)  # Size for the icon labels
            c.setFillColor(colors.HexColor("#424242"))  # Same color as heading
        
        # Position text to the right of the icon
            text_x = x_pos + icon_size + 15  # Spacing between icon and text
        
        # Calculate heights for better vertical centering
            line_height = 35 # Height for each line of text
            text_height_total = 60  # Total height for both lines
            line_gap = 12 # Gap between lines
            
            vertical_adjustment = -18
        
            first_line_y = icon_center_y + (line_height + line_gap)/2 + vertical_adjustment # First line position
            second_line_y = icon_center_y - (line_height - line_gap)/2 + vertical_adjustment # Second line position
        
        # Draw first line (BRAND)
            c.drawString(text_x, first_line_y, icon_texts[i][0])
        
        # Draw second line (VISUALS/PERSONALITY/POSITIONING)
            c.drawString(text_x, second_line_y, icon_texts[i][1])
    
        draw_footer_cta()


    def Recommendations_Page(content):
        from textwrap import wrap
        import re

        c.showPage()
        draw_header()

    # --- Pink Sticker ---
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # --- Heading ---
        heading_font = "Anton"
        heading_size = 50
        heading_text = "RECOMMENDATIONS"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, heading_y - 20, LEFT_MARGIN + heading_width, heading_y - 20)

    # --- Parse Content Dynamically ---
        sanitized = sanitize_text(content).strip()
        recommendations = []

    # Try to extract with **Title** format
        pattern = re.findall(r"\*\*(.*?)\*\*\n(.+?)(?:\n\n|$)", sanitized, re.DOTALL)
        if pattern:
            for title, desc in pattern:
                recommendations.append({
                    "title": title.strip(),
                    "body": desc.strip().replace("\n", " ")
                })
        else:
        # Fallback: Split plain paragraph into 3 equal parts
            chunks = re.split(r"\n{2,}", sanitized)
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
            chunk_len = len(chunks)

            if chunk_len >= 3:
                for i in range(3):
                    lines = chunks[i].split("\n", 1)
                    title = lines[0].strip()
                    body = lines[1].strip() if len(lines) > 1 else ""
                    recommendations.append({
                        "title": title,
                        "body": body
                   })
            else:
            # fallback again: break into 3 word blocks
                words = sanitized.split()
                chunk_size = len(words) // 3
                for i in range(3):
                    start = i * chunk_size
                    end = (i + 1) * chunk_size if i < 2 else len(words)
                    chunk = " ".join(words[start:end])
                    recommendations.append({
                        "title": f"Tip {i+1}",
                        "body": chunk.strip()
                   })

    # --- Draw boxes ---
        #box_width = (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - 40) / 3
        gap_between_boxes = 30  # increase this for more spacing
        box_width = (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - (gap_between_boxes * 2)) / 3

        box_top_y = heading_y - 130
        lime_color = colors.HexColor("#c1ff72")
        text_color = colors.HexColor("#424242")
        #title_style.textColor = colors.HexColor("#424242")

        # --- Layout Settings ---
        gap_between_boxes = 30
        box_padding = 12
        box_width = (PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - (2 * gap_between_boxes)) / 3
        box_top_y = heading_y - 130
        box_height = 130

        title_box_height = 48

        lime_color = colors.HexColor("#c1ff72")
        text_color = colors.HexColor("#000000")

        body_style = ParagraphStyle(

            name='Body',
            fontName='Helvetica',
            fontSize=14,
            leading=16,
            textColor=text_color,
            alignment=TA_LEFT,
            spaceAfter=0
        )

        title_style = ParagraphStyle(
            name='Title',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=14,
            textColor=text_color,
            alignment=TA_LEFT
        )

        for i, rec in enumerate(recommendations[:3]):
            x = LEFT_MARGIN + i * (box_width + gap_between_boxes)
            y = box_top_y

    # --- Lime Title Box ---
            c.setFillColor(lime_color)
            text_color = colors.HexColor("#000000")
            c.roundRect(x, y, box_width, title_box_height, 6, stroke=0, fill=1)

            title_paragraph = Paragraph(rec["title"], title_style)


            title_frame = Frame(
                x + box_padding,          # x
                y + 2,                   # y (bump higher inside green box)
                box_width - 2 * box_padding,
                title_box_height - 10,    # height reduced to fit inside box
                showBoundary=0
            ) 
            title_frame.addFromList([title_paragraph], c)

            body_paragraph = Paragraph(rec["body"], body_style)
            body_frame = Frame(
                x + box_padding,
                y - title_box_height - 40,
                box_width - 2 * box_padding,
                box_height - title_box_height,
                showBoundary=0
            )
            body_frame.addFromList([body_paragraph], c)            

            draw_footer_cta()
    
    def Next_Steps_page():
        c.showPage()

    # --- Header: Logo + Pink Line ---
        if os.path.exists(LOGO_PATH):
            logo_y = LOGO_Y_OFFSET
            c.drawImage(LOGO_PATH, LEFT_MARGIN, LOGO_Y_OFFSET, width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')

            line_start = LEFT_MARGIN + LOGO_WIDTH + 10
            line_y = logo_y + LOGO_HEIGHT / 2
            c.setStrokeColor(colors.HexColor("#ef1fb3"))
            c.setLineWidth(4)
            c.line(line_start, line_y, PAGE_WIDTH - RIGHT_MARGIN, line_y)

    # --- Pink Sticker ---
        sticker_text = "D2C PROFIT LEAK AUDIT"
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.HexColor("#ef1fb3"))
        sticker_width = c.stringWidth(sticker_text, "Helvetica-Bold", 16) + 20
        c.roundRect(LEFT_MARGIN, PAGE_HEIGHT - 2.2 * inch, sticker_width, 35, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.drawString(LEFT_MARGIN + 10, PAGE_HEIGHT - 2.2 * inch + 12, sticker_text)

    # --- Heading ---
        heading_font = "Anton"
        heading_size = 50
        heading_text = "NEXT STEPS"
        heading_y = PAGE_HEIGHT - 3.2 * inch

        c.setFont(heading_font, heading_size)
        c.setFillColor(colors.HexColor("#424242"))
        c.drawString(LEFT_MARGIN, heading_y, heading_text)

        heading_width = c.stringWidth(heading_text, heading_font, heading_size)
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(LEFT_MARGIN, heading_y - 20, LEFT_MARGIN + heading_width, heading_y - 20)

    # --- Replace single image with 3 icon images with text beside them in 2 lines ---
        icon_paths = [
            os.path.join(BASE_DIR,"..", "assets", "marketing_audit_icon.png"),
            os.path.join(BASE_DIR,"..", "assets", "data_audit_icon.png"),
            os.path.join(BASE_DIR,"..", "assets", "gameplan_proposal_icon.png")
        ]
    
    # Text in two parts: [first line, second line]
        icon_texts = [
            ["MARKETING", "AUDIT"], 
            ["DATA", "AUDIT"], 
            ["GAMEPLAN &", "PROPOSAL"]
        ]
    
    # Set up dimensions
        icon_size = 80  # Size of each circular icon
        total_width = PAGE_WIDTH - (2 * LEFT_MARGIN)  # Available width
    
    # Starting Y position below the blue line
        icon_top_y = heading_y - 120
        icon_center_y = icon_top_y  # Center point of the icon
    
    # Draw each icon with text beside it
        for i in range(3):
        # Calculate starting position for each group
            if i == 0:
                x_pos = LEFT_MARGIN
            else:
                x_pos = LEFT_MARGIN + (i * 280)  # Evenly space the three groups
        
        # Draw circle with lime green background for icon
            c.setFillColor(colors.HexColor("#c5ff54"))  # Lime green color from the image
            c.circle(x_pos + (icon_size/2), icon_center_y, icon_size/2, fill=1, stroke=0)  # No stroke
        
        # Try to draw icon image
            if os.path.exists(icon_paths[i]):
                c.drawImage(icon_paths[i], x_pos, icon_center_y - (icon_size/2), width=icon_size, height=icon_size, mask='auto')
            else:
                print(f"[!] Icon image not found: {icon_paths[i]}")
        
        # Draw text beside icon using same font as heading
            c.setFont(heading_font, 30)  # Size for the icon labels
            c.setFillColor(colors.HexColor("#424242"))  # Same color as heading
        
        # Position text to the right of the icon
            text_x = x_pos + icon_size + 15  # Spacing between icon and text
        
        # Calculate heights for better vertical centering
            line_height = 35 # Height for each line of text
            text_height_total = 60  # Total height for both lines
            line_gap = 12 # Gap between lines
            
            vertical_adjustment = -18
        
        # Calculate vertical positions for perfect centering
            #first_line_y = icon_center_y + 12
            #econd_line_y = icon_center_y - 18
            first_line_y = icon_center_y + (line_height + line_gap)/2 + vertical_adjustment # First line position
            second_line_y = icon_center_y - (line_height - line_gap)/2 + vertical_adjustment # Second line position
        
        # Draw first line (BRAND)
            c.drawString(text_x, first_line_y, icon_texts[i][0])
        
        # Draw second line (VISUALS/PERSONALITY/POSITIONING)
            c.drawString(text_x, second_line_y, icon_texts[i][1])
    
        draw_footer_cta()    


    def draw_section(title, content, is_list=False):
        c.showPage()
        draw_header()
        draw_heading_on_left(title)
        # --- Blue Divider ---
        divider_x = PAGE_WIDTH * 0.4
        c.setStrokeColor(colors.HexColor("#007FFF"))
        c.setLineWidth(8)
        c.line(divider_x, BOTTOM_MARGIN, divider_x, PAGE_HEIGHT - 1.5 * inch)

        # --- Content Style & Frame ---
        content_style = ParagraphStyle(
            'content',
            fontName='Helvetica',
            fontSize=15,
            leading=18,
            textColor=colors.black,
            alignment=0  #aligned left
        )

        frame_x = divider_x + 20
        frame_width = PAGE_WIDTH - frame_x - RIGHT_MARGIN
        frame_max_height = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN
                
        story = []
        if is_list and isinstance(content, list):
            grouped = {}
            for item in content:
                heading = sanitize_text(item.get('heading', ''))
                desc = sanitize_text(item.get('description', ''))
                grouped.setdefault(heading, []).append(desc)

            for heading, descriptions in grouped.items():
                #story.append(Paragraph(f"<b>{heading}</b>", content_style))
                #story.append(Spacer(1, 8))
                for desc in descriptions:
                    full_line = f"<b>{heading}:</b> {desc}"
                    story.append(Paragraph(full_line, content_style))
                    #story.append(Paragraph(desc, content_style))
                    story.append(Spacer(1, 6))
                #story.append(Spacer(1, 12))
        else:
            sanitized = sanitize_text(content)
            paragraphs = sanitized.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), content_style))
                    story.append(Spacer(1, 12))


        dummy_canvas = canvas.Canvas("temp.pdf")
        kf = KeepInFrame(frame_width, frame_max_height, story)
        story_width, story_height = kf.wrapOn(dummy_canvas, frame_width, frame_max_height)

# --- Step 2: Center vertically within available height ---
        # --- Step 1: Accurately calculate story height ---
        dummy_canvas = canvas.Canvas("temp.pdf")
        story_copy = list(story)  # to avoid mutating original list
        story_height = 0
        for flowable in story_copy:
            _, h = flowable.wrap(frame_width, frame_max_height)
            story_height += h

# --- Step 2: Calculate vertical Y position to center ---
        frame_height = story_height + 40
        frame_y = BOTTOM_MARGIN + (frame_max_height - story_height) / 2

# --- Step 3: Use normal Frame (no KeepInFrame!) to render story directly ---
        frame = Frame(frame_x, frame_y, frame_width, frame_height, showBoundary=0)
        frame.addFromList(story, c)

        draw_footer_cta()


    def parse_swot(swot_text):
        swot_items = []
        current_category = None
        #seen_categories = set()
        for line in swot_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('**Strengths**'):
                current_category = 'Strengths'
            elif line.startswith('**Weaknesses**'):
                current_category = 'Weaknesses'
            elif line.startswith('**Opportunities**'):
                current_category = 'Opportunities'
            elif line.startswith('**Threats**'):
                current_category = 'Threats'
            elif current_category:
                swot_items.append({
                    'heading': current_category,
                    'description': line.replace('**', '').strip()
                })
            
        return swot_items

    def parse_porter(porter_text):
        porter_items = []
        current_category = None
        #seen_categories = set()
        for line in porter_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('**Competitors**'):
                current_category = 'Competitors'
            elif line.startswith('**Threat of New Competitors**'):
                current_category = 'Threat of New Competitors'
            elif line.startswith('**Threat of Substitutes**'):
                current_category = 'Threat of Substitutes'
            elif line.startswith('**Supplier Power**'):
                current_category = 'Supplier Power'
            elif line.startswith('**Customer Power**'):
                current_category = 'Customer Power'
            elif current_category:
                porter_items.append({
                    'heading': current_category,
                    'description': line.replace('**', '').strip()
                })
        return porter_items
    
    def parse_porter_page(porter_text):
        porter_items = []
        current_category = None
        buffer = ""

        for line in porter_text.split('\n'):
            line = line.strip()
            if not line:
                continue

        # Detect category changes
            if line.startswith('**Competitors**'):
                if current_category and buffer:
                    porter_items.append({
                        'heading': current_category,
                        'description': buffer.strip().replace('**', '')
                    })
                    buffer = ""
                current_category = 'Competitors'

            elif line.startswith('**Threat of New Competitors**'):
                if current_category and buffer:
                    porter_items.append({
                        'heading': current_category,
                        'description': buffer.strip().replace('**', '')
                    })
                    buffer = ""
                current_category = 'Threat of New Competitors'

            elif line.startswith('**Threat of Substitutes**'):
                if current_category and buffer:
                    porter_items.append({
                        'heading': current_category,
                        'description': buffer.strip().replace('**', '')
                    })
                    buffer = ""
                current_category = 'Threat of Substitutes'

            elif line.startswith('**Supplier Power**'):
                if current_category and buffer:
                    porter_items.append({
                        'heading': current_category,
                        'description': buffer.strip().replace('**', '')
                    })
                    buffer = ""
                current_category = 'Supplier Power'

            elif line.startswith('**Customer Power**'):
                if current_category and buffer:
                    porter_items.append({
                        'heading': current_category,
                        'description': buffer.strip().replace('**', '')
                    })
                    buffer = ""
                current_category = 'Customer Power'

            elif current_category:
                buffer += " " + line.replace('**', '')

    # Don't forget to append the last one
        if current_category and buffer:
            porter_items.append({
                'heading': current_category,
                'description': buffer.strip().replace('**', '')
            })

        return porter_items

    
    def copy_gap_analysis(copy_gap_text):
        copy_gap_items = []
        current_category = None
        #seen_categories = set()
        for line in copy_gap_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('**Clarity of Structure**'):
                current_category = 'Clarity of Structure'
            elif line.startswith('**Emotional & Logical Persuasion**'):
                current_category = 'Emotional & Logical Persuasion'
            elif line.startswith('**Relevance to Target Audience**'):
                current_category = 'Relevance to Target Audience'
            elif line.startswith('**Strong CTA Alignment**'):
                current_category = 'Strong CTA Alignment'
            elif line.startswith('**Proof & Credibility Integration**'):
                current_category = 'Proof & Credibility Integration'
            elif line.startswith('**Score**'):
                current_category = 'Score'
            elif current_category:
                copy_gap_items.append({
                    'heading': current_category,
                    'description': line.replace('**', '').strip()
                })

        return copy_gap_items
    
    def copy_gap_analysis_page1(copy_gap_text):
        copy_gap_items = []

    # Match headings like **Title** followed by description
        pattern = re.findall(r"\*\*(.*?)\*\*\:?\s*(.*?)(?=(\n\*\*|$))", copy_gap_text, re.DOTALL)

        for heading, desc, _ in pattern:
            heading = heading.strip()
            desc = desc.replace('\n', ' ').strip()
        
        # Normalize Score heading if embedded
            if 'score' in heading.lower():
                heading = "Score"

            copy_gap_items.append({
                "heading": heading,
                "description": desc
            })

        return copy_gap_items


    # intro page
    brand_name = responses.get("brand_name", "the brand")
    #draw_intro_page(brand_name)

    # All Sections
    #if 'branding_messaging' in responses:
        #draw_section("BRANDING & MESSAGING", responses['branding_messaging'])
    # 1. BRANDING & MESSAGING
    draw_intro_page(brand_name, responses.get("branding_messaging", ""))

    # 2. Executive Summary
    if 'executive_summary' in responses:
        draw_section("EXECUTIVE SUMMARY", responses['executive_summary'])

    #Business_Model_Analysis()
    Business_Model_Analysis_page()    
    draw_section("BUSINESS DESCRIPTION", responses.get("business_description", ''))
    draw_section("REVENUE MODEL", responses.get("revenue_model", ''))
    draw_section("TARGET AUDIENCE", responses.get("target_audience", ''))

    if 'swot_analysis' in responses:
        draw_section("SWOT ANALYSIS", parse_swot(responses['swot_analysis']), is_list=True)

    if 'porter_analysis' in responses:
        draw_section("PORTER'S 5 FORCES", parse_porter_page(responses['porter_analysis']), is_list=True)

    
    Copy_Analysis_page()
    draw_section("IDEAL COPY STYLE", responses.get("ideal_copy_style", ''))
    if 'copy_gap_analysis' in responses:
        draw_section("COPY GAP ANALYSIS", copy_gap_analysis_page1(responses['copy_gap_analysis']), is_list=True)

    draw_section("COPY SUGGESTIONS", responses.get("copy_suggestions", ''))
    Brand_Analysis_page()
    draw_section("BRAND VISUALS", responses.get("brand_visuals", ''))
    draw_section("BRAND PERSONALITY", responses.get("brand_personality", ''))
    draw_section("BRAND POSITIONING", responses.get("brand_positioning", ''))
    
    Recommendations_Page(responses.get("recommendations", ''))

    Next_Steps_page()    
    c.save()
    print(f"PDF saved to: {file_path}")
    return file_path
