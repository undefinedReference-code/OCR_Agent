import re

def postprocess_ocr_result(text: str) -> str:
    """Simplified math formula format conversion"""
    print("[OCR] Converting LaTeX math format to Markdown format...")
    
    # Since formula internals won't have \(, any \( ... \) should be treated as complete math expressions
    
    # 1. Convert display math formulas \[ ... \] to $$ ... $$
    text = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'$$\1$$', text, flags=re.DOTALL)
    
    # 2. Convert inline math formulas \( ... \) to $ ... $
    # Since formula internals won't have \(, we can safely replace directly
    text = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'$\1$', text, flags=re.DOTALL)
    
    # 3. Clean up formatting
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    return text.strip()