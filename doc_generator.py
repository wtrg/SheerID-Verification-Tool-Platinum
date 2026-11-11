"""
Enhanced Document Generator with "Scan" Effects and Photorealism
"""
import random
import time
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

# Try to load standard fonts, fallback to default
def get_font(size, bold=False):
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
        "verdanab.ttf" if bold else "verdana.ttf"
    ]
    for font_path in possible_fonts:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    return ImageFont.load_default()

def add_scan_effect(img):
    """
    Simulates a scanned document or phone photo
    """
    # 1. Add noise
    img = img.convert("RGB")
    pixels = img.load()
    for _ in range(img.size[0] * img.size[1] // 5):
        x, y = random.randint(0, img.size[0]-1), random.randint(0, img.size[1]-1)
        r, g, b = pixels[x, y]
        noise = random.randint(-15, 15)
        pixels[x, y] = (
            max(0, min(255, r + noise)),
            max(0, min(255, g + noise)),
            max(0, min(255, b + noise))
        )
        
    # 2. Slight Blur (Simulate bad focus)
    if random.random() > 0.5:
        img = img.filter(ImageFilter.BoxBlur(0.5))
        
    # 3. Rotate slightly (Not perfectly straight scan)
    angle = random.uniform(-1.5, 1.5)
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True, fillcolor=(255, 255, 255))
    
    # 4. Color Grading (Make it look not purely digital white)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.8) # Desaturate slightly
    
    # 5. Lighting Gradient (Shadow)
    overlay = Image.new('RGBA', img.size, (0,0,0,0))
    ctx = ImageDraw.Draw(overlay)
    # Simulate shadow from phone/scanner
    ctx.rectangle([0, 0, img.width, img.height], fill=(20, 20, 20, 10))
    img.paste(overlay, (0,0), overlay)
    
    return img

def generate_student_id(first, last, school):
    """
    Generates a realistic-looking Student ID card
    """
    width, height = 800, 500
    color = random.choice([(0, 51, 102), (102, 0, 0), (0, 102, 51), (51, 51, 51)])
    
    img = Image.new("RGB", (width, height), (245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # Header Background
    draw.rectangle([0, 0, width, 120], fill=color)
    
    # Text
    draw.text((400, 60), school.upper(), fill=(255, 255, 255), anchor="mm", font=get_font(40, bold=True))
    draw.text((400, 200), "STUDENT IDENTITY CARD", fill=(0, 0, 0), anchor="mm", font=get_font(25))
    
    # Photo placeholder
    draw.rectangle([50, 150, 250, 400], outline=(0,0,0), width=2)
    draw.text((150, 275), "PHOTO", fill=(100,100,100), anchor="mm", font=get_font(20))
    
    # Details
    info_x = 300
    draw.text((info_x, 250), f"Name: {first.upper()} {last.upper()}", fill=(0, 0, 0), font=get_font(30, bold=True))
    draw.text((info_x, 300), f"ID No: {random.randint(10000000, 99999999)}", fill=(0, 0, 0), font=get_font(25))
    draw.text((info_x, 350), f"Issued: {time.strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=get_font(25))
    draw.text((info_x, 400), f"Valid Thru: {int(time.strftime('%Y')) + 4}", fill=(0, 0, 0), font=get_font(25))
    
    # Barcode simulation
    draw.rectangle([50, 430, 750, 480], fill=(0,0,0))
    for i in range(20):
        x = random.randint(50, 750)
        draw.rectangle([x, 430, x+5, 480], fill=(255,255,255))

    # Apply Effects
    final_img = add_scan_effect(img)
    
    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

def generate_transcript(first, last, dob, school):
    """
    Generates a realistic-looking Unofficial Transcript
    """
    width, height = 1000, 1400 # A4-ish ratio
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Header
    draw.text((500, 80), school.upper(), fill=(0, 0, 0), anchor="mm", font=get_font(45, bold=True))
    draw.text((500, 140), "OFFICIAL ACADEMIC TRANSCRIPT", fill=(50, 50, 50), anchor="mm", font=get_font(30))
    draw.line((100, 160, 900, 160), fill=(0,0,0), width=2)
    
    # Student Info
    draw.text((100, 200), "STUDENT INFORMATION", fill=(0,0,0), font=get_font(25, bold=True))
    draw.text((100, 240), f"Name: {last.upper()}, {first.upper()}", fill=(0,0,0), font=get_font(20))
    draw.text((100, 270), f"Date of Birth: {dob}", fill=(0,0,0), font=get_font(20))
    draw.text((100, 300), f"Student ID: {random.randint(100000000, 999999999)}", fill=(0,0,0), font=get_font(20))
    
    draw.text((550, 240), f"Print Date: {time.strftime('%Y-%m-%d')}", fill=(0,0,0), font=get_font(20))
    draw.text((550, 270), "Standing: Good Standing", fill=(0,0,0), font=get_font(20))
    
    # Grades Table
    start_y = 400
    draw.rectangle([100, start_y, 900, start_y+40], fill=(230, 230, 230))
    headers = ["Course Code", "Course Title", "Credits", "Grade"]
    positions = [120, 300, 700, 820]
    
    for i, h in enumerate(headers):
        draw.text((positions[i], start_y+10), h, fill=(0,0,0), font=get_font(18, bold=True))
        
    courses = [
        ("CS 101", "Intro to Computer Science", "4.00", "A"),
        ("ENG 102", "Academic Writing", "3.00", "A-"),
        ("MATH 201", "Calculus I", "4.00", "B+"),
        ("HIST 110", "World History", "3.00", "A"),
        ("PHY 105", "General Physics", "4.00", "B"),
        ("ART 100", "Art Appreciation", "3.00", "A")
    ]
    
    y = start_y + 50
    for code, title, cred, grade in courses:
        draw.text((positions[0], y), code, fill=(0,0,0), font=get_font(18))
        draw.text((positions[1], y), title, fill=(0,0,0), font=get_font(18))
        draw.text((positions[2], y), cred, fill=(0,0,0), font=get_font(18))
        draw.text((positions[3], y), grade, fill=(0,0,0), font=get_font(18))
        y += 35
        
    draw.line((100, y+20, 900, y+20), fill=(0,0,0), width=2)
    draw.text((700, y+40), "Term GPA: 3.75", fill=(0,0,0), font=get_font(20, bold=True))
    draw.text((700, y+70), "Cum GPA: 3.75", fill=(0,0,0), font=get_font(20, bold=True))
    
    # Watermark/Seal (Simulated)
    draw.ellipse([700, 1000, 900, 1200], outline=(200, 200, 200), width=5)
    draw.text((800, 1100), "OFFICIAL", fill=(200, 200, 200), anchor="mm", font=get_font(30))
    
    # Scan effect
    final_img = add_scan_effect(img)

    buf = BytesIO()
    final_img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()

def select_document_type():
    return "student_id" if random.random() < 0.3 else "transcript" # Transcripts often have higher success rate
