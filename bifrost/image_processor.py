import cv2
import numpy as np
import easyocr
import logging
import os
from PIL import Image
from io import BytesIO
import base64

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reader = easyocr.Reader(['en'], gpu=False)

# Utility to convert image file to OpenCV image
def load_image(file_path):
    logger.info(f"Loading image from {file_path}")
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError("Invalid image format or corrupted file")
    return image

# Convert image to grayscale and denoise
def preprocess_image(image):
    logger.info("Preprocessing image...")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshed = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return threshed

# Detect text regions using EasyOCR
def extract_text_from_image(image):
    logger.info("Extracting text using EasyOCR...")
    results = reader.readtext(image)
    texts = []
    for bbox, text, conf in results:
        if conf > 0.4:  # Confidence threshold
            texts.append({'text': text, 'bbox': bbox})
    logger.info(f"Detected {len(texts)} text blocks.")
    return texts

# Detect rectangles and contours
def extract_contours_from_image(image):
    logger.info("Extracting layout contours...")
    edged = cv2.Canny(image, 30, 150)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    logger.info(f"Found {len(contours)} contours.")
    return contours

# Resize image proportionally
def resize_image(image, max_width=800):
    h, w = image.shape[:2]
    if w > max_width:
        ratio = max_width / float(w)
        image = cv2.resize(image, (max_width, int(h * ratio)))
    return image

# Draw bounding boxes for visualization
def draw_text_boxes(image, text_data):
    logger.info("Drawing text bounding boxes...")
    for item in text_data:
        bbox = np.int32(item['bbox'])
        cv2.polylines(image, [bbox], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.putText(image, item['text'], tuple(bbox[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
    return image

# Convert image to base64 for web preview
def encode_image_to_base64(image):
    logger.info("Encoding image to base64...")
    _, buffer = cv2.imencode('.png', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/png;base64,{encoded_image}"

# High-level image processing pipeline
def process_uploaded_image(image_path, framework='vanilla', css_type='external'):
    logger.info("Starting image processing pipeline...")

    try:
        image = load_image(image_path)
        resized = resize_image(image)
        preprocessed = preprocess_image(resized)

        logger.info("Image resized and preprocessed.")

        text_data = extract_text_from_image(resized)
        contours = extract_contours_from_image(preprocessed)
        components = detect_ui_components(resized)
        annotated_image = draw_text_boxes(resized.copy(), text_data)

        logger.info(f"Texts detected: {len(text_data)} | Contours: {len(contours)} | Components: {len(components)}")

        html_code, _, _ = generate_code(
            text_data=text_data,
            contours=contours,
            components=components,
            framework=framework,
            css_type=css_type
        )

        base64_img = encode_image_to_base64(annotated_image)

        logger.info("Image processing complete.")

        return {
            "html_code": html_code,
            "annotated_image": base64_img,
            "texts": text_data,
            "contours": len(contours),
            "components": components
        }

    except Exception as e:
        logger.error(f"Error during image processing: {str(e)}")
        raise


# Extra utilities if needed

def save_image(image, path):
    logger.info(f"Saving image to {path}")
    cv2.imwrite(path, image)

def convert_image_to_png_bytes(image):
    logger.info("Converting image to PNG byte stream...")
    is_success, buffer = cv2.imencode(".png", image)
    if not is_success:
        raise ValueError("Image conversion failed")
    return BytesIO(buffer)

def clean_temp_files(path):
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info(f"Temporary file {path} deleted.")
    except Exception as e:
        logger.warning(f"Failed to delete {path}: {str(e)}")

# Add to image_processing.py

def detect_ui_components(image):
    """Detect common UI components like buttons, inputs, etc."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    components = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)
        
        # Detect buttons (rectangles with specific aspect ratio)
        if 2.5 > aspect_ratio > 0.4 and w > 30 and h > 10:
            components.append({
                'type': 'button',
                'x': x,
                'y': y,
                'width': w,
                'height': h
            })
            
        # Detect input fields (wide rectangles)
        elif aspect_ratio > 3 and w > 100:
            components.append({
                'type': 'input',
                'x': x,
                'y': y,
                'width': w,
                'height': h
            })
    
    return components

def generate_code(text_data, contours, components, framework='vanilla', css_type='external'):
    """Enhanced code generator with framework support"""
    
    html_parts = ["<!DOCTYPE html>\n<html>\n<head>\n<title>Generated UI</title>"]
    css_parts = ["<style>"]
    js_parts = ["<script>"]
    
    # Base styles
    css_parts.append("""
    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
    .container { position: relative; width: 100%; min-height: 100vh; }
    """)
    
    # Generate HTML structure
    html_parts.append("</head>\n<body>\n<div class=\"container\">")
    
    # 1. Add contours as divs
    for i, contour in enumerate(contours):
        x, y, w, h = cv2.boundingRect(contour)
        html_parts.append(f'<div class="box-{i}"></div>')
        css_parts.append(f".box-{i} {{ position: absolute; left: {x}px; top: {y}px; width: {w}px; height: {h}px; border: 1px solid #ddd; }}")
    
    #2. Add text elements
    for i, text in enumerate(text_data):
        bbox = np.array(text['bbox'])  # convert list of points to NumPy array
        x = int(np.min(bbox[:, 0]))
        y = int(np.min(bbox[:, 1]))
        html_parts.append(f'<div class="text-{i}">{text["text"]}</div>')
        css_parts.append(f".text-{i} {{ position: absolute; left: {x}px; top: {y}px; }}")

    # 3. Add detected components
    for i, comp in enumerate(components):
        if comp['type'] == 'button':
            html_parts.append(f'<button class="btn-{i}">Button</button>')
            css_parts.append(f""".btn-{i} {{
                position: absolute;
                left: {comp['x']}px;
                top: {comp['y']}px;
                width: {comp['width']}px;
                height: {comp['height']}px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
            }}""")
        elif comp['type'] == 'input':
            html_parts.append(f'<input class="input-{i}" placeholder="Input field">')
            css_parts.append(f""".input-{i} {{
                position: absolute;
                left: {comp['x']}px;
                top: {comp['y']}px;
                width: {comp['width']}px;
                height: {comp['height']}px;
                padding: 8px;
                border: 1px solid #ddd;
            }}""")
    
    # Close tags
    html_parts.append("</div>\n</body>\n</html>")
    css_parts.append("</style>")
    js_parts.append("</script>")
    
    # Framework specific processing
    if framework == 'react':
        # Transform to React component
        html = "import React from 'react';\n\nexport default function GeneratedUI() {\n  return (\n"
        html += "\n".join(html_parts[4:-2])  # Skip doctype and basic tags
        html += "\n  );\n}"
        css = css_parts[0] + "\n".join(css_parts[1:-1]) + "\n" + css_parts[-1]
        return html, css, ""
    
    return "\n".join(html_parts), "\n".join(css_parts), "\n".join(js_parts)