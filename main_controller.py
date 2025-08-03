from main_view import MainView
import keyboard
import pyautogui
import time

class MainController:
    def __init__(self):
        self.mainView = MainView()
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
        
        # Register hotkey
        keyboard.add_hotkey('f1', self.start_screenshot)
        print("[Controller] OCR screenshot tool initialized")
        
    def start_screenshot(self):
        """Start screenshot capture process"""
        if self.is_capturing:
            return
            
        print("[Controller] Starting screenshot capture")
        self.is_capturing = True
        
        # Small delay to ensure hotkey release
        time.sleep(0.1)
        
        # Take full screen screenshot
        self.screenshot = pyautogui.screenshot()
        print("[Controller] Screenshot captured")
        
        # Create capture window through view
        self.mainView.create_capture_window(self.screenshot)
        self.mainView.start_main_loop()
        
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
            if abs(right - left) > 5 and abs(bottom - top) > 5:
                self.selected_area = (left, top, right, bottom)
                
                width = right - left
                height = bottom - top
                
                self.mainView.show_selection_info(width, height)
                print(f"[Controller] Area selected: {width}x{height} pixels")
                
    def on_keyboard_cancel(self, event):
        """Handle ESC key - cancel operation"""
        print("[Controller] Cancel operation")
        self.cancel_screenshot()
        
    def on_keyboard_confirm(self, event):
        """Handle Enter key - confirm selection"""
        print("[Controller] Confirm selection")
        if self.selected_area:
            print(f"[Controller] Processing selected area: {self.selected_area}")
            # TODO: Process OCR here
            self.close_capture_window()
        else:
            print("[Controller] No area selected")
            self.cancel_screenshot()
            
    def cancel_screenshot(self):
        """Cancel screenshot operation"""
        print("[Controller] Screenshot operation cancelled")
        self.close_capture_window()
        
    def close_capture_window(self):
        """Close capture window and reset state"""
        self.mainView.close_capture_window()
        self.is_capturing = False
        self.start_x = None
        self.start_y = None
        self.selected_area = None
        self.screenshot = None
        print("[Controller] Capture window closed, state reset")

    def run(self):
        """Run OCR screenshot tool"""
        try:
            print("[Controller] OCR screenshot tool running...")
            print("Press F1 to start screenshot and OCR recognition")
            print("Press Ctrl+C to exit")
            
            keyboard.wait('ctrl+c')
            
        except KeyboardInterrupt:
            print("\n[Controller] Program exited")
        except Exception as e:
            print(f"[Controller] Program error: {e}")