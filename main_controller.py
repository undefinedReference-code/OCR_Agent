import threading
import time
import keyboard
import pyautogui
from main_view import MainView
from ocr_service import OCRService

class MainController:
    def __init__(self):
        self.mainView = MainView()
        self.ocrService = OCRService()  # Add OCR service
        self.screenshot = None
        self.start_x = None
        self.start_y = None
        self.selected_area = None
        self.is_capturing = False
        
        # Setup event handlers
        event_handlers = {
            'mouse_down': self.on_mouse_down,
            'mouse_drag': self.on_mouse_drag,
            'mouse_up': self.on_mouse_up,
            'keyboard_cancel': self.on_keyboard_cancel,
            'keyboard_confirm': self.on_keyboard_confirm
        }
        
        self.mainView.setup_event_handlers(event_handlers)
        
        print("[Controller] OCR screenshot tool initialized")
        
    def _setup_hotkey(self):
        """Setup hotkey monitoring in separate thread"""
        keyboard.add_hotkey('f1', self.start_screenshot)
        print("[Controller] F1 hotkey registered")
        
        # Keep hotkey monitoring active
        try:
            keyboard.wait()  # Wait for hotkey events
        except KeyboardInterrupt:
            print("[Controller] Hotkey monitoring stopped")
    
    def start_screenshot(self):
        """Start screenshot capture process"""
        if self.is_capturing:
            print("[Controller] Screenshot already in progress, skipping")
            return
            
        print("[Controller] Starting screenshot capture")
        self.is_capturing = True
        
        # Small delay to ensure hotkey release
        time.sleep(0.1)
        
        # Take full screen screenshot
        self.screenshot = pyautogui.screenshot()
        print(f"[Controller] Screenshot captured, size: {self.screenshot.size}")
        
        # Create capture window through view (execute in main thread)
        self.mainView.root.after(0, lambda: self.mainView.create_capture_window(self.screenshot))
        
    def on_mouse_down(self, event):
        """Handle mouse down event"""
        self.start_x = event.x
        self.start_y = event.y
        self.mainView.delete_current_rect()
        print(f"[Controller] Mouse down at ({event.x}, {event.y})")
            
    def on_mouse_drag(self, event):
        """Handle mouse drag event"""
        if self.start_x is not None and self.start_y is not None:
            self.mainView.delete_current_rect()
            self.mainView.draw_rect(self.start_x, self.start_y, event.x, event.y)
            
    def on_mouse_up(self, event):
        """Handle mouse up event"""
        if self.start_x is not None and self.start_y is not None:
            end_x, end_y = event.x, event.y
            
            # Calculate rectangle bounds
            left = min(self.start_x, end_x)
            top = min(self.start_y, end_y)
            right = max(self.start_x, end_x)
            bottom = max(self.start_y, end_y)
            
            # Validate selection size
            width = abs(right - left)
            height = abs(bottom - top)
            
            if width > 5 and height > 5:
                self.selected_area = (left, top, right, bottom)
                print(f"[Controller] Valid area selected: {width}x{height} pixels")
                self.mainView.show_selection_info(width, height)
            else:
                print(f"[Controller] Area too small: {width}x{height} pixels (minimum 5x5)")
                
    def on_keyboard_cancel(self, event):
        """Handle ESC key - cancel operation"""
        print("[Controller] Cancel operation triggered")
        self.cancel_screenshot()
        
    def on_keyboard_confirm(self, event):
        """Handle Enter key - confirm selection"""
        print("[Controller] Confirm selection triggered")
        if self.selected_area:
            print(f"[Controller] Processing selected area: {self.selected_area}")
            self.process_selected_area()
        else:
            print("[Controller] No area selected, cancelling")
            self.cancel_screenshot()
            
    def process_selected_area(self):
        """Process selected screenshot area"""
        print("[Controller] Starting to process selected area")
        
        # Add validation with clear error messages
        if not self.screenshot:
            raise ValueError("No screenshot available - this should not happen")
        
        if not self.selected_area:
            raise ValueError("No area selected - this should not happen")
        
        print(f"[Controller] Screenshot size: {self.screenshot.size}")
        print(f"[Controller] Selected area: {self.selected_area}")
        
        # Extract selected area from screenshot
        cropped_image = self.screenshot.crop(self.selected_area)
        print(f"[Controller] Cropped image size: {cropped_image.size}")
        
        # Close capture window first (only UI cleanup)
        print("[Controller] Closing capture window")
        self.close_capture_window()
        
        # Show screenshot preview in new window
        print("[Controller] Showing screenshot preview")
        self.mainView.show_screenshot_preview(cropped_image, self.selected_area)
        
        # Start OCR recognition asynchronously
        print("[Controller] Starting OCR recognition")
        self.start_ocr_recognition(cropped_image)
        
        # Reset controller state after preview is shown
        print("[Controller] Resetting controller state")
        self.reset_controller_state()
    
    def start_ocr_recognition(self, image):
        """Start OCR recognition for the cropped image"""
        def ocr_callback(result):
            """Callback function to handle OCR result"""
            print(f"[Controller] OCR recognition completed")
            # Update view with OCR result (execute in main thread)
            if self.mainView.root:
                self.mainView.root.after(0, lambda: self.mainView.update_ocr_result(result))
        
        # Start async OCR recognition
        self.ocrService.recognize_async(image, ocr_callback)
         
    def cancel_screenshot(self):
        """Cancel screenshot operation"""
        print("[Controller] Screenshot operation cancelled")
        self.close_capture_window()
        self.reset_controller_state()
        
    def close_capture_window(self):
        """Close capture window (UI only)"""
        print("[Controller] Closing capture window")
        
        # Close view window - this might fail if window is already closed
        if self.mainView:
            self.mainView.close_capture_window()
        
        # Only reset capturing flag
        self.is_capturing = False
        
        print("[Controller] Capture window closed")

    def reset_controller_state(self):
        """Reset controller state data"""
        print("[Controller] Resetting controller state")
        
        self.start_x = None
        self.start_y = None
        self.selected_area = None
        self.screenshot = None
        
        print("[Controller] Controller state reset")

    def run(self):
        """Run OCR screenshot tool"""
        print("[Controller] OCR screenshot tool running...")
        print("Press F1 to start screenshot and OCR recognition")
        print("Press Ctrl+C to exit")
        
        # Create main window
        self.mainView.create_main_window()
        
        # Start hotkey monitoring in separate thread
        hotkey_thread = threading.Thread(target=self._setup_hotkey, daemon=True)
        hotkey_thread.start()
        
        # Start main event loop
        try:
            self.mainView.start_main_loop()
        except KeyboardInterrupt:
            print("\n[Controller] Program exited by user")
        finally:
            self.mainView.close_all_windows()