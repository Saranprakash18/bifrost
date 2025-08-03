import cv2
import numpy as np
import easyocr
import logging
import os
import base64
import re
from PIL import Image
from collections import defaultdict

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.min_confidence = 0.7  # Higher confidence threshold
        self.min_component_area = 1000
        self.max_aspect_ratio = 5.0

    def load_image(self, file_path):
        """Load image with multiple fallback methods"""
        try:
            # Try OpenCV first
            image = cv2.imread(file_path)
            if image is not None:
                return image
            
            # Fallback to PIL if OpenCV fails
            with Image.open(file_path) as pil_img:
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                
        except Exception as e:
            logger.error(f"Image loading failed: {str(e)}")
            raise ValueError(f"Unsupported image format or corrupted file: {str(e)}")

    def preprocess_image(self, image):
        """Advanced image preprocessing pipeline"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            contrast = clahe.apply(gray)
            
            # Denoising
            denoised = cv2.fastNlMeansDenoising(contrast, h=15, 
                                              templateWindowSize=7, 
                                              searchWindowSize=21)
            
            # Adaptive thresholding
            thresh = cv2.adaptiveThreshold(denoised, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            raise

    def extract_text_regions(self, image):
        """Advanced text extraction with layout analysis"""
        try:
            # Get text with detailed layout information
            results = self.reader.readtext(image, 
                                         paragraph=True, 
                                         detail=1,
                                         batch_size=4,
                                         text_threshold=0.7,
                                         link_threshold=0.4,
                                         width_ths=0.5,
                                         height_ths=0.5)
            
            text_blocks = []
            for item in results:
                if len(item) < 3:
                    continue
                    
                bbox, text, conf = item[:3]
                if conf < self.min_confidence:
                    continue
                
                # Clean and validate text
                cleaned_text = self.clean_text(text)
                if not cleaned_text:
                    continue
                
                # Calculate precise bounding box
                x_min = min(p[0] for p in bbox)
                x_max = max(p[0] for p in bbox)
                y_min = min(p[1] for p in bbox)
                y_max = max(p[1] for p in bbox)
                
                text_blocks.append({
                    'text': cleaned_text,
                    'bbox': bbox,
                    'x': x_min,
                    'y': y_min,
                    'width': x_max - x_min,
                    'height': y_max - y_min,
                    'confidence': conf
                })
            
            return text_blocks
            
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise

    def clean_text(self, text):
        """Advanced text cleaning"""
        if not isinstance(text, str):
            return ""
            
        # Remove special characters but preserve common UI characters
        text = re.sub(r'[^\w\s\-_@#&*$%+=<>/\\:;,.?!]', '', text.strip())
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text if len(text) > 1 else ""

    def detect_ui_components(self, image):
        """Advanced UI component detection with ML-inspired heuristics"""
        try:
            # Edge detection with Canny
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5,5), 0)
            edges = cv2.Canny(blurred, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            components = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < self.min_component_area:
                    continue
                    
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = w / float(h)
                
                # Skip components with extreme aspect ratios
                if aspect_ratio > self.max_aspect_ratio or aspect_ratio < 1/self.max_aspect_ratio:
                    continue
                
                # Calculate solidity (area/convex hull area)
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = float(area)/hull_area if hull_area > 0 else 0
                
                # Classify component type based on features
                component = self.classify_component(x, y, w, h, aspect_ratio, solidity)
                if component:
                    components.append(component)
            
            return components
            
        except Exception as e:
            logger.error(f"Component detection failed: {str(e)}")
            raise

    def classify_component(self, x, y, w, h, aspect_ratio, solidity):
        """Classify UI components using heuristic rules"""
        # Button detection
        if 0.8 < aspect_ratio < 3.5 and 1000 < w*h < 50000 and solidity > 0.85:
            return {
                'type': 'button',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'text': ''
            }
            
        # Input field detection
        elif aspect_ratio > 3 and w*h > 2000 and solidity > 0.7:
            return {
                'type': 'input',
                'x': x,
                'y': y,
                'width': w,
                'height': h,
                'text': ''
            }
            
        # Card/container detection
        elif w*h > 10000 and solidity > 0.6:
            return {
                'type': 'container',
                'x': x,
                'y': y,
                'width': w,
                'height': h
            }
            
        return None

    def match_text_to_components(self, components, text_blocks):
        """Match text blocks to their parent components"""
        try:
            # Create a spatial index for faster lookup
            from rtree import index
            idx = index.Index()
            
            for i, comp in enumerate(components):
                idx.insert(i, (comp['x'], comp['y'], 
                          comp['x'] + comp['width'], 
                          comp['y'] + comp['height']))
            
            # Match text to components
            for text in text_blocks:
                if not isinstance(text, dict) or 'x' not in text:
                    continue
                    
                # Find all components that contain this text
                matches = list(idx.intersection((text['x'], text['y'], 
                                               text['x'] + text['width'], 
                                               text['y'] + text['height'])))
                
                # Assign to the smallest matching component
                if matches:
                    smallest_area = float('inf')
                    best_match = None
                    
                    for match_idx in matches:
                        comp = components[match_idx]
                        area = comp['width'] * comp['height']
                        if area < smallest_area:
                            smallest_area = area
                            best_match = comp
                    
                    if best_match and 'text' in best_match:
                        best_match['text'] = text['text']
            
            return components
            
        except ImportError:
            # Fallback without R-tree
            for comp in components:
                if 'text' not in comp:
                    continue
                    
                for text in text_blocks:
                    if not isinstance(text, dict) or 'x' not in text:
                        continue
                        
                    if (comp['x'] <= text['x'] <= comp['x'] + comp['width'] and
                        comp['y'] <= text['y'] <= comp['y'] + comp['height']):
                        comp['text'] = text['text']
                        break
                        
            return components

    def generate_html_css(self, components, text_blocks, framework='vanilla', css_type='external'):
        """Generate semantic HTML/CSS based on detected components"""
        try:
            # Match text to components first
            components = self.match_text_to_components(components, text_blocks)
            
            # Initialize code containers
            html = []
            css = []
            
            # HTML boilerplate
            html.append('<!DOCTYPE html>')
            html.append('<html lang="en">')
            html.append('<head>')
            html.append('  <meta charset="UTF-8">')
            html.append('  <meta name="viewport" content="width=device-width, initial-scale=1.0">')
            html.append('  <title>Generated UI</title>')
            
            if css_type == 'external':
                html.append('  <link rel="stylesheet" href="styles.css">')
            else:
                html.append('  <style>')
            
            # Base CSS
            css_base = """/* Generated by Bifrost */
:root {
  --primary-color: #0078d4;
  --hover-color: #106ebe;
  --text-color: #323130;
  --border-color: #d1d1d1;
  --bg-color: #f5f5f5;
  --white: #ffffff;
  --shadow: 0 2px 4px rgba(0,0,0,0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

body {
  background-color: var(--bg-color);
  color: var(--text-color);
  line-height: 1.5;
  padding: 24px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  min-height: 100vh;
}
"""
            if css_type == 'inline':
                html.append(css_base)
            
            # Generate component code
            for i, comp in enumerate(components):
                if comp['type'] == 'button':
                    html.append(f'    <button class="btn btn-{i}">{comp.get("text", "Button")}</button>')
                    css.append(f"""
.btn-{i} {{
  position: absolute;
  left: {comp['x']}px;
  top: {comp['y']}px;
  width: {comp['width']}px;
  height: {comp['height']}px;
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}}

.btn-{i}:hover {{
  background-color: var(--hover-color);
}}
""")
                elif comp['type'] == 'input':
                    html.append(f'    <div class="input-group input-{i}">')
                    if comp.get('text'):
                        html.append(f'      <label>{comp["text"]}</label>')
                    html.append(f'      <input type="text" placeholder="{comp.get("text", "")}">')
                    html.append('    </div>')
                    css.append(f"""
.input-{i} {{
  position: absolute;
  left: {comp['x']}px;
  top: {comp['y']}px;
  width: {comp['width']}px;
}}

.input-{i} label {{
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-color);
}}

.input-{i} input {{
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}}

.input-{i} input:focus {{
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(0, 120, 212, 0.1);
}}
""")
                elif comp['type'] == 'container':
                    html.append(f'    <div class="card card-{i}">')
                    html.append('      <!-- Card content would go here -->')
                    html.append('    </div>')
                    css.append(f"""
.card-{i} {{
  position: absolute;
  left: {comp['x']}px;
  top: {comp['y']}px;
  width: {comp['width']}px;
  height: {comp['height']}px;
  background-color: var(--white);
  border-radius: 8px;
  box-shadow: var(--shadow);
  padding: 16px;
}}
""")
            
            # Add standalone text blocks
            for i, text in enumerate(text_blocks):
                if not any(comp['x'] <= text['x'] <= comp['x'] + comp['width'] and 
                          comp['y'] <= text['y'] <= comp['y'] + comp['height'] 
                          for comp in components):
                    html.append(f'    <div class="text-block text-{i}">{text["text"]}</div>')
                    css.append(f"""
.text-{i} {{
  position: absolute;
  left: {text['x']}px;
  top: {text['y']}px;
  font-size: {max(12, int(text['height'] * 0.7))}px;
  color: var(--text-color);
}}
""")
            
            # Close HTML tags
            if css_type == 'inline':
                html.append('  </style>')
            html.append('</head>')
            html.append('<body>')
            html.append('  <div class="container">')
            html.append('  </div>')
            html.append('</body>')
            html.append('</html>')
            
            # Prepare final output
            if css_type == 'external':
                full_css = css_base + "\n".join(css)
            else:
                full_css = ""
                
            return "\n".join(html), full_css
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise

    def process_uploaded_image(self, image_path, framework='vanilla', css_type='external'):
        """Complete image processing pipeline"""
        try:
            # Load and validate image
            image = self.load_image(image_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Detect components and text
            text_blocks = self.extract_text_regions(image)
            components = self.detect_ui_components(image)
            
            # Generate code
            html_code, css_code = self.generate_html_css(components, text_blocks, framework, css_type)
            
            # Create annotated preview
            annotated = self.create_annotated_preview(image, components, text_blocks)
            base64_img = self.image_to_base64(annotated)
            
            return {
                'html_code': html_code,
                'css_code': css_code,
                'js_code': self.generate_javascript(components, framework),
                'annotated_image': base64_img,
                'success': True,
                'components': components,
                'text_blocks': text_blocks
            }
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            return {
                'html_code': f'<!-- Processing error: {str(e)} -->',
                'css_code': f'/* Processing error: {str(e)} */',
                'js_code': f'// Processing error: {str(e)}',
                'annotated_image': '',
                'success': False,
                'error': str(e)
            }

    def create_annotated_preview(self, image, components, text_blocks):
        """Create visualization of detected elements"""
        annotated = image.copy()
        
        # Draw components
        for comp in components:
            color_map = {
                'button': (0, 255, 0),    # Green
                'input': (255, 0, 0),     # Red
                'container': (0, 0, 255)  # Blue
            }
            color = color_map.get(comp.get('type', ''), (128, 128, 128))
            cv2.rectangle(annotated, 
                         (comp['x'], comp['y']), 
                         (comp['x'] + comp['width'], comp['y'] + comp['height']), 
                         color, 2)
            cv2.putText(annotated, 
                       comp.get('type', 'unknown'), 
                       (comp['x'], comp['y'] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw text blocks
        for text in text_blocks:
            if isinstance(text, dict) and 'bbox' in text:
                points = np.array(text['bbox'], dtype=np.int32)
                cv2.polylines(annotated, [points], True, (255, 165, 0), 2)  # Orange
        
        return annotated

    def image_to_base64(self, image):
        """Convert image to base64 with error handling"""
        try:
            _, buffer = cv2.imencode('.png', image)
            return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"
        except Exception as e:
            logger.error(f"Failed to encode image: {str(e)}")
            return ""

    def generate_javascript(self, components, framework):
        """Generate framework-specific JavaScript"""
        if framework == 'react':
            return """import React from 'react';
import './styles.css';

export default function GeneratedUI() {
  return (
    <div className="container">
      {/* Generated components will be rendered here */}
    </div>
  );
}
"""
        else:
            return """document.addEventListener('DOMContentLoaded', function() {
  // Add interactivity to generated components
  const buttons = document.querySelectorAll('.btn');
  
  buttons.forEach(button => {
    button.addEventListener('click', function() {
      console.log('Button clicked:', this.textContent);
    });
  });
});
"""

# Global processor instance
processor = ImageProcessor()

def process_uploaded_image(image_path, framework='vanilla', css_type='external'):
    """Wrapper function for the image processor"""
    return processor.process_uploaded_image(image_path, framework, css_type)