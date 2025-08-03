from typing import Callable, Dict
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import ImageTk, Image
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
        self.preview_window = None
        self.capture_toplevel = None

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
            
    def create_main_window(self):
        """Create main application window (hidden root window)"""
        if self.root is None:
            print("[View] Creating main application window")
            self.root = tk.Tk()
            self.root.title("OCR Screenshot Tool")
            # Hide main window, only used as root window
            self.root.withdraw()
            print("[View] Main application window created (hidden)")
            
    def create_capture_window(self, screenshot):
        """Create fullscreen capture window with screenshot background"""
        print("[View] Creating capture window")
        
        # Ensure main window exists
        self.create_main_window()
        
        # If capture window already exists, close it first
        if self.capture_toplevel:
            try:
                self.capture_toplevel.destroy()
            except:
                pass
            self.capture_toplevel = None
        
        # Create capture window as Toplevel
        self.capture_toplevel = tk.Toplevel(self.root)
        self.capture_toplevel.title("OCR Screenshot Tool - Select Area")
        
        # Get screen dimensions
        screen_width = self.capture_toplevel.winfo_screenwidth()
        screen_height = self.capture_toplevel.winfo_screenheight()
        self.capture_toplevel.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Set window properties
        self.capture_toplevel.attributes('-topmost', True)
        self.capture_toplevel.attributes('-alpha', 0.3)
        self.capture_toplevel.configure(bg='black')
        self.capture_toplevel.overrideredirect(True)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.capture_toplevel, 
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
        self._bind_keyboard_events_to_capture_window()
        
        # Set focus
        self.capture_toplevel.focus_set()
        
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
    
    def _bind_keyboard_events_to_capture_window(self):
        """
        Bind keyboard events to Root window - Solve focus management issues
        
        Why bind to Root:
        1. Root window is a natural focus manager
        2. Global keyboard shortcut response (ESC, Enter)
        3. Does not depend on specific component focus state
        4. Better user experience
        """
        print(f"[View] Binding keyboard events to capture window")
        
        if not self.capture_toplevel:
            print("[View] Error: Capture window not created")
            return
        
        # Bind keyboard events to capture window using injected handler functions
        if self._keyboard_handlers['cancel']:
            self.capture_toplevel.bind('<Escape>', self._keyboard_handlers['cancel'])
            print(f"[View] ESC key event bound to capture window")
        
        if self._keyboard_handlers['confirm']:
            self.capture_toplevel.bind('<Return>', self._keyboard_handlers['confirm'])
            print(f"[View] Enter key event bound to capture window")
            
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
            text=f"已选择区域: {width}x{height} 像素\n按回车开始识别，ESC取消",
            fill='yellow',
            font=('Arial', 14)
        )
        print(f"[View] Selection info displayed: {width}x{height} pixels")

    def clear_selection_info(self):
        """Clear selection area information"""
        if hasattr(self, 'info_text_id') and self.info_text_id:
            self.canvas.delete(self.info_text_id)
            self.info_text_id = None
            
    def show_screenshot_preview(self, cropped_image, selected_area):
        """Show screenshot preview in new window"""
        print("[View] Creating screenshot preview window")
        
        # Ensure main window exists
        self.create_main_window()
        
        # If preview window already exists, close it first
        if self.preview_window:
            try:
                self.preview_window.destroy()
            except:
                pass
            self.preview_window = None
        
        # Create preview window as Toplevel
        self.preview_window = tk.Toplevel(self.root)
        self.preview_window.title("截图预览 - Screenshot Preview")
        
        # Calculate window size based on image size
        img_width, img_height = cropped_image.size
        
        # Set maximum window size
        max_width = 800
        max_height = 600
        
        # Calculate display size while maintaining aspect ratio
        if img_width > max_width or img_height > max_height:
            ratio = min(max_width / img_width, max_height / img_height)
            display_width = int(img_width * ratio)
            display_height = int(img_height * ratio)
            # Resize image for display
            display_image = cropped_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            display_width = img_width
            display_height = img_height
            display_image = cropped_image
        
        # Set window size (add padding for UI elements)
        window_width = display_width + 40
        window_height = display_height + 120
        
        # Center window on screen
        screen_width = self.preview_window.winfo_screenwidth()
        screen_height = self.preview_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.preview_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.preview_window.resizable(False, False)
        
        # Create main frame
        main_frame = tk.Frame(self.preview_window, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info label
        left, top, right, bottom = selected_area
        info_text = f"截图区域: {right-left}x{bottom-top} 像素 | 位置: ({left}, {top}) 到 ({right}, {bottom})"
        info_label = tk.Label(
            main_frame, 
            text=info_text,
            font=('Arial', 10),
            bg='white',
            fg='gray'
        )
        info_label.pack(pady=(0, 10))
        
        # Image display frame
        image_frame = tk.Frame(main_frame, bg='white', relief=tk.SUNKEN, bd=2)
        image_frame.pack(pady=(0, 10))
        
        # Convert PIL image to PhotoImage and display
        self.preview_image = ImageTk.PhotoImage(display_image)
        image_label = tk.Label(image_frame, image=self.preview_image, bg='white')
        image_label.pack(padx=5, pady=5)
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        # Save button
        save_button = tk.Button(
            button_frame,
            text="保存图片",
            command=lambda: self._save_screenshot(cropped_image),
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            padx=20,
            relief=tk.FLAT
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # OCR button (placeholder for future implementation)
        ocr_button = tk.Button(
            button_frame,
            text="开始OCR识别",
            command=lambda: self._start_ocr_processing(cropped_image),
            bg='#2196F3',
            fg='white',
            font=('Arial', 10),
            padx=20,
            relief=tk.FLAT
        )
        ocr_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_button = tk.Button(
            button_frame,
            text="关闭",
            command=self._close_preview_window,
            bg='#f44336',
            fg='white',
            font=('Arial', 10),
            padx=20,
            relief=tk.FLAT
        )
        close_button.pack(side=tk.RIGHT)
        
        # Bind window close event
        self.preview_window.protocol("WM_DELETE_WINDOW", self._close_preview_window)
        
        # Set window properties
        self.preview_window.attributes('-topmost', True)
        self.preview_window.focus_set()
        
        print(f"[View] Screenshot preview window created: {img_width}x{img_height} pixels")

    def _close_preview_window(self):
        """Safely close preview window"""
        if self.preview_window:
            try:
                print("[View] Closing preview window")
                self.preview_window.destroy()
            except Exception as e:
                print(f"[View] Error closing preview window: {e}")
            finally:
                self.preview_window = None
                self.preview_image = None
            
    def _save_screenshot(self, image):
        """Save screenshot to file"""
        try:
            from tkinter import filedialog
            from datetime import datetime
            
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"screenshot_{timestamp}.png"
            
            # Open save dialog
            filename = filedialog.asksaveasfilename(
                title="保存截图",
                defaultextension=".png",
                initialname=default_filename,
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if filename:
                image.save(filename)
                messagebox.showinfo("保存成功", f"截图已保存到:\n{filename}")
                print(f"[View] Screenshot saved to: {filename}")
            else:
                print("[View] Save operation cancelled")
                
        except Exception as e:
            error_msg = f"保存失败: {str(e)}"
            messagebox.showerror("保存失败", error_msg)
            print(f"[View] Save error: {e}")
    
    def _start_ocr_processing(self, image):
        """Start OCR processing (placeholder)"""
        print("[View] OCR processing requested")
        messagebox.showinfo("OCR功能", "OCR识别功能将在后续版本中实现")
        # TODO: Implement OCR processing here
            
    def close_capture_window(self):
        """Close capture window only"""
        if self.capture_toplevel:
            print("[View] Closing capture window")
            try:
                self.capture_toplevel.destroy()
            except Exception as e:
                print(f"[View] Error closing capture window: {e}")
            finally:
                self.capture_toplevel = None
                self.canvas = None
                self.bg_image = None
                self.rect_id = None

    def close_all_windows(self):
        """Close all windows for program exit"""
        print("[View] Closing all windows")
        
        # Close preview window
        self._close_preview_window()
        
        # Close capture window
        self.close_capture_window()
        
        # Close main window
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception as e:
                print(f"[View] Error closing main window: {e}")
            finally:
                self.root = None