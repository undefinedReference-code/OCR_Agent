


from typing import Callable
from addict import Dict


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
        
    def _store_event_handlers(self, event_handlers: Dict[str, Callable]):
        """
        Store event handler functions - Core of dependency injection
        
        This injects Controller methods into View without creating circular reference
        """
        print(f"[View] Storing event handler functions")
        
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
            print(f"[View] All event handler functions ready")
            
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
            print(f"[View] Error: Canvas not created")
            return
        
        # Bind mouse events to Canvas using injected handler functions
        if self._mouse_handlers['down']:
            self.canvas.bind('<Button-1>', self._mouse_handlers['down'])
            print(f"[View] Mouse down event bound to Canvas")
        
        if self._mouse_handlers['drag']:
            self.canvas.bind('<B1-Motion>', self._mouse_handlers['drag'])
            print(f"[View] Mouse drag event bound to Canvas")
        
        if self._mouse_handlers['up']:
            self.canvas.bind('<ButtonRelease-1>', self._mouse_handlers['up'])
            print(f"[View] Mouse release event bound to Canvas")
    
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
            print(f"[View] Error: Root window not created")
            return
        
        # Bind keyboard events to Root window using injected handler functions
        if self._keyboard_handlers['cancel']:
            self.root.bind('<Escape>', self._keyboard_handlers['cancel'])
            print(f"[View] ESC key event bound to Root window")
        
        if self._keyboard_handlers['confirm']:
            self.root.bind('<Return>', self._keyboard_handlers['confirm'])
            print(f"[View] Enter key event bound to Root window")
            
    def delete_current_rect(self):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def draw_rect(self, start_x, start_y, end_x, end_y):
        self.rect_id = self.canvas.create_rectangle(
            start_x, start_y, end_x, end_y,
            outline='red', width=2, fill='', stipple='gray50'
        )