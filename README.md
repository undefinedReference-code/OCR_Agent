# OCR Agent

An intelligent OCR (Optical Character Recognition) screenshot tool with system tray integration, featuring automatic LaTeX to Markdown conversion and background operation.

## 🚀 Features

- **Intelligent OCR**: Powered by Ollama with vision language models
- **LaTeX to Markdown**: Automatic conversion of mathematical formulas

## 📋 Requirements

### System Requirements
- Python 3.7+
- Ollama server running locally

### Python Dependencies
```
requests>=2.25.0
keyboard>=0.13.5
pyautogui>=0.9.54
pillow>=8.0.0
pystray>=0.19.0
psutil>=5.8.0
```

### Ollama Setup
1. Install [Ollama](https://ollama.ai/)
2. Pull a vision language model:
   ```bash
   ollama pull qwen2.5-vl:7b
   ```
3. Ensure Ollama is running on `http://localhost:11434`

## 🎯 Usage

### Starting the Application
```bash
python main.py
```

### Basic Operations

#### Taking Screenshots
- **Method 1**: Press `F1` (global hotkey)
- **Method 2**: Right-click tray icon → "OCR Screenshot (F1)"

#### Screenshot Workflow
1. Press F1 to start screenshot mode
2. Drag mouse to select OCR area
3. Press `Enter` to confirm selection
4. Press `ESC` to cancel anytime

#### Managing the Application
- **Check Status**: Press `ESC` or tray menu → "Show Status"
- **Exit Application**: Right-click tray icon → "Exit"

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `F1` | Start screenshot capture |
| `ESC` | Cancel operation / Show status |
| `Enter` | Confirm area selection |
| `Drag` | Select OCR area |

## 🏗️ Architecture

### Project Structure
```
OCR_Agent/
├── main.py                    # Application entry point
├── main_controller.py         # Main application controller
├── main_view.py              # UI components and windows
├── ocr_service.py            # OCR API integration
├── ocr_postprocess.py        # LaTeX to Markdown conversion
├── system_tray.py            # System tray management
├── requirements.txt          # Python dependencies
└── README.md                # Project documentation
```

### Core Components

#### MainController
- Manages application lifecycle
- Handles global hotkeys
- Coordinates between UI and services
- Thread-safe command queue system

#### MainView
- Screenshot capture window
- Results preview interface
- Tkinter-based UI components

#### OCRService
- Ollama API integration
- Asynchronous OCR processing
- Base64 image encoding

#### SystemTrayManager
- Background operation
- Tray icon and menu
- User interaction handling

## ⚙️ Configuration

### OCR Settings
Edit `ocr_service.py` to customize:
```python
class OCRService:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5-vl:7b"  # Change model here
        self.timeout = 600  # Request timeout in seconds
```

### UI Settings
Modify appearance in `main_view.py`:
```python
# Window transparency
self.capture_toplevel.attributes('-alpha', 0.3)

# Selection color and width
self.canvas.create_rectangle(..., outline='red', width=2)
```

## 🔧 Advanced Features

### LaTeX Formula Conversion
The application automatically converts LaTeX math notation:
- `\( formula \)` → `$ formula $` (inline)
- `\[ formula \]` → `$$ formula $$` (block)

## 🐛 Troubleshooting

#### Ollama Connection Failed
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```
