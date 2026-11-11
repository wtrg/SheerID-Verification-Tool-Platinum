from PIL import Image, ImageDraw, ImageFilter; import random; import numpy as np;
def add_noise(img):
    if img.mode != 'RGB': img = img.convert('RGB')
    arr = np.array(img).astype(np.float32)
    noise = np.random.normal(0, 4, arr.shape)
    noisy_arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_arr)
def add_glitch(img):
    angle = random.uniform(-1.0, 1.0)
    return img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
def draw_avatar_silhouette(draw, box):
    x1, y1, x2, y2 = box
    w, h = x2-x1, y2-y1
    draw.rectangle([x1, y1, x2, y2], fill=(215, 215, 220), outline=(180, 180, 180))
    sil_color = (80, 80, 85)
    head_size = int(w * 0.45)
    draw.ellipse([x1+w//2-head_size//2, y1+int(h*0.35)-head_size//2, x1+w//2+head_size//2, y1+int(h*0.35)+head_size//2], fill=sil_color)
    draw.chord([x1+w//2-int(w*0.85)//2, y1+int(h*0.85)-int(h*0.5)//2, x1+w//2+int(w*0.85)//2, y1+int(h*0.85)+int(h*0.5)//2], start=180, end=0, fill=sil_color)
