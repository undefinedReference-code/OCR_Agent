from typing import Callable, Dict
import tkinter as tk
from PIL import ImageTk
import pyautogui

class MainView:
    def __init__(self):
        self.controller = None
        self.capture_window = None
        self.canvas = None
        self.processing_window = None
        self.result_window = None
        self.result_text = None
        self.bg_image = None
        self.rect_id = None
        self.root = None
        
    def setup_event_handlers(self, event_handlers: Dict[str, Callable]):
        """Public interface to setup event handlers"""
        self._store_event_handlers(event_handlers)
        
    def _store_event_handlers(self, event_handlers: Dict[str, Callable]):
        """Store event handler functions - Core of dependency injection"""
        print("[View] Storing event handler functions")
        
        # Separate mouse and keyboard event handler functions
        self._mouse_handlers = {
            'down': event_handlers.get('mouse_down'),
            'drag': event_handlers.get('mouse_drag'),
            'up': event_handlers.get('mouse_up')
        }
        
        self._keyboard_handlers = {
            'cancel': event_handlers.get('keyboard_cancel'),
            'confirm': event_handlers.get('keyboard_confirm')
        }
        
        # Validate required handler functions
        required_handlers = ['mouse_down', 'mouse_drag', 'mouse_up', 'keyboard_cancel', 'keyboard_confirm']
        missing_handlers = [h for h in required_handlers if h not in event_handlers or event_handlers[h] is None]
        
        if missing_handlers:
            print(f"[View] Warning: Missing event handler functions: {missing_handlers}")
        else:
            print("[View] All event handler functions ready")
            
    def create_capture_window(self, screenshot):
        """Create fullscreen capture window with screenshot background"""
        print("[View] Creating capture window")
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("OCR Screenshot Tool - Select Area")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Set window properties
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        self.root.overrideredirect(True)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=screen_width, 
            height=screen_height,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack()
        
        # Set screenshot as background
        self.bg_image = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # Bind events
        self._bind_mouse_events_to_canvas()
        self._bind_keyboard_events_to_root()
        
        # Set focus
        self.root.focus_set()
        
        # Show instruction text
        self.canvas.create_text(
            screen_width//2, 50, 
            text="拖拽鼠标框选需要OCR识别的区域，回车开始识别，ESC取消", 
            fill='white', 
            font=('Arial', 16)
        )
        
        print("[View] Capture window created successfully")
        
    def start_main_loop(self):
        """Start tkinter main loop"""
        if self.root:
            print("[View] Starting main loop")
            self.root.mainloop()
        
    def _bind_mouse_events_to_canvas(self):
        """
        Bind mouse events to Canvas - Solve coordinate system issues
        
        Why bind to Canvas:
        1. Mouse events need precise coordinate information
        2. Canvas is the actual drawing area
        3. event.x, event.y are relative to Canvas coordinate system
        4. Convenient for directly drawing selection rectangle on Canvas
        """
        print(f"[View] Binding mouse events to Canvas")
        
        if not self.canvas:
            print("[View] Error: Canvas not created")
            return
        
        if self._mouse_handlers['down']:
            self.canvas.bind('<Button-1>', self._mouse_handlers['down'])
        
        if self._mouse_handlers['drag']:
            self.canvas.bind('<B1-Motion>', self._mouse_handlers['drag'])
        
        if self._mouse_handlers['up']:
            self.canvas.bind('<ButtonRelease-1>', self._mouse_handlers['up'])
    
    def _bind_keyboard_events_to_root(self):
        """
        Bind keyboard events to Root window - Solve focus management issues
        
        Why bind to Root:
        1. Root window is a natural focus manager
        2. Global keyboard shortcut response (ESC, Enter)
        3. Does not depend on specific component focus state
        4. Better user experience
        """
        print(f"[View] Binding keyboard events to Root window")
        
        if not self.root:
            print("[View] Error: Root window not created")
            return
        
        # Bind keyboard events to Root window using injected handler functions
        if self._keyboard_handlers['cancel']:
            self.root.bind('<Escape>', self._keyboard_handlers['cancel'])
            print(f"[View] ESC key event bound to Root window")
        
        if self._keyboard_handlers['confirm']:
            self.root.bind('<Return>', self._keyboard_handlers['confirm'])
            print(f"[View] Enter key event bound to Root window")
            
    def delete_current_rect(self):
        """Delete current selection rectangle"""
        if self.rect_id and self.canvas:
            self.canvas.delete(self.rect_id)
            self.rect_id = None
    
    def draw_rect(self, start_x, start_y, end_x, end_y):
        """Draw selection rectangle"""
        if self.canvas:
            self.rect_id = self.canvas.create_rectangle(
                start_x, start_y, end_x, end_y,
                outline='red', width=2, fill='', stipple='gray50'
            )
        else:
            print("[View] Error: Canvas not available for drawing rectangle")
        
    def show_selection_info(self, width, height):
        """Display selection area information"""
        if not self.canvas or not self.root:
            print("[View] Error: Canvas or Root not available")
            return
        
        # Remove previous info text if exists
        if hasattr(self, 'info_text_id') and self.info_text_id:
            self.canvas.delete(self.info_text_id)
        
        # Display new selection info
        screen_center_x = self.root.winfo_screenwidth() // 2
        self.info_text_id = self.canvas.create_text(
            screen_center_x, 100,
            text=f"已选择区域: {width}x{height} 像素\n按回车开始OCR识别，ESC取消",
            fill='yellow',
            font=('Arial', 14)
        )
        print(f"[View] Selection info displayed: {width}x{height} pixels")

    def clear_selection_info(self):
        """Clear selection area information"""
        if hasattr(self, 'info_text_id') and self.info_text_id:
            self.canvas.delete(self.info_text_id)
            self.info_text_id = None
            
    def close_capture_window(self):
        """Close capture window"""
        if self.root:
            print("[View] Closing capture window")
            self.root.quit()
            self.root.destroy()
            self.root = None
            self.canvas = None
            self.bg_image = None
            self.rect_id = None