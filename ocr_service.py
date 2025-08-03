import requests
import base64
import threading
from io import BytesIO
from typing import Callable, Optional

class OCRService:
    def __init__(self):
        # Ollama API configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5vl:7b"
        
    def image_to_base64(self, image):
        """Convert PIL image to base64 encoding"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def call_ollama_ocr(self, image_base64: str) -> str:
        """Call Ollama API for OCR recognition"""
        try:
            prompt = """Please perform OCR text recognition on the image and strictly follow these output requirements:
1. Output format: Pure Markdown format
2. Preserve original paragraph structure and line breaks
3. Mathematical formula format requirements (Important):
   - Inline math formulas must use: $ formula content $
   - Block math formulas must use: $$ formula content $$
   - Do NOT use \\( \\) format! Must convert to $ $ format
   - Do NOT use \\[ \\] format! Must convert to $$ $$ format
4. Format conversion examples:
   Wrong: \\( E[X] = \\mu \\) → Correct: $ E[X] = \\mu $
   Wrong: \\[ \\int f(x)dx \\] → Correct: $$ \\int f(x)dx $$
5. Other requirements:
   - Do not add any explanations or comments
   - Ignore excess line breaks that OCR might produce
   - Maintain semantic coherence
   - Output recognition results directly

Please strictly follow the above format requirements for output."""
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=600)
            
            if response.status_code == 200:
                result = response.json()
                print("[OCR] Recognition successful")
                return result.get('response', 'Recognition failed: No response content')
            else:
                return f"API call failed: Status code {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Connection failed: Please ensure Ollama service is running (http://localhost:11434)"
        except requests.exceptions.Timeout:
            return "Request timeout: OCR recognition took too long"
        except Exception as e:
            return f"OCR recognition error: {str(e)}"
    
    def recognize_async(self, image, callback: Callable[[str], None]):
        """Perform OCR recognition asynchronously"""
        def ocr_worker():
            try:
                print("[OCR] Starting async recognition")
                # Convert image to base64
                image_base64 = self.image_to_base64(image)
                
                # Call Ollama for OCR
                result = self.call_ollama_ocr(image_base64)
                
                # Execute callback with result
                callback(result)
                
            except Exception as e:
                error_msg = f"OCR recognition failed: {str(e)}"
                callback(error_msg)
        
        # Start OCR in background thread
        thread = threading.Thread(target=ocr_worker, daemon=True)
        thread.start()
        print("[OCR] Background OCR thread started")