import tkinter as tk
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import threading
import sys
import os

class SystemTrayManager:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.tray_icon = None
        self.is_running = True
    
    
    def create_tray_icon(self):
        """Create system tray icon"""
        # Create a simple icon
        image = self.create_icon_image()
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("OCR Screenshot (F1)", self.start_screenshot),
            pystray.MenuItem("Show Status", self.show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings", self.show_settings),
            pystray.MenuItem("History", self.show_history),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("About", self.show_about),
            pystray.MenuItem("Exit", self.quit_application)
        )
        
        # Create tray icon
        self.tray_icon = pystray.Icon(
            "OCR_Agent",
            image,
            "OCR Screenshot Tool",
            menu
        )
        
        return self.tray_icon
    
    def create_icon_image(self):
        """Create tray icon image"""
        # Create a 64x64 icon
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw a simple OCR icon
        # Outer frame
        draw.rectangle([8, 8, width-8, height-8], outline='blue', width=3)
        
        # Text "OCR"
        try:
            # Try to use system font
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        text = "OCR"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill='blue', font=font)
        
        return image
    
    def start_screenshot(self, icon=None, item=None):
        """Start screenshot from tray menu"""
        print("[Tray] Starting screenshot from tray menu")
        if self.main_controller:
            self.main_controller.start_screenshot()
    
    def show_status(self, icon=None, item=None):
        """Show status information"""
        if self.main_controller:
            self.main_controller._show_status_info()
        
        # Also show in tray notification
        if self.tray_icon:
            status = "Ready for screenshot" if not self.main_controller.is_capturing else "Capturing..."
            self.tray_icon.notify("OCR Agent Status", status)
    
    def show_settings(self, icon=None, item=None):
        """Show settings window"""
        print("[Tray] Opening settings (not implemented yet)")
        if self.tray_icon:
            self.tray_icon.notify("Settings", "Settings window coming soon!")
    
    def show_history(self, icon=None, item=None):
        """Show history window"""
        print("[Tray] Opening history (not implemented yet)")
        if self.tray_icon:
            self.tray_icon.notify("History", "History window coming soon!")
    
    def show_about(self, icon=None, item=None):
        """Show about information"""
        # Create a temporary Tkinter window for about dialog
        def show_about_dialog():
            root = tk.Tk()
            root.withdraw()  # Hide main window
            
            about_text = """OCR Screenshot Tool v1.0
            
An intelligent OCR tool with screenshot capability.

Features:
• F1 - Start screenshot
• ESC - Cancel operation
• Automatic LaTeX to Markdown conversion
• System tray integration

Developer: Your Name
"""
            messagebox.showinfo("About OCR Agent", about_text)
            root.destroy()
        
        # Execute in main thread
        threading.Thread(target=show_about_dialog, daemon=True).start()
    
    def quit_application(self, icon=None, item=None):
        """Quit application"""
        print("[Tray] Quit application requested")
        
        # Confirm exit
        def confirm_quit():
            root = tk.Tk()
            root.withdraw()
            
            result = messagebox.askyesno(
                "Confirm Exit", 
                "Are you sure you want to exit OCR Agent?\n\nThe application will stop running in the background."
            )
            
            if result:
                print("[Tray] User confirmed exit")
                if self.tray_icon:
                    self.tray_icon.stop()
                
                # Cleanup main controller
                if self.main_controller:
                    self.main_controller.quit_threaded()
                
                # Force exit
                os._exit(0)
            else:
                print("[Tray] User cancelled exit")
            
            root.destroy()
        
        threading.Thread(target=confirm_quit, daemon=True).start()
    
    def run_tray(self):
        """Run system tray"""
        print("[Tray] Starting system tray")
        tray_icon = self.create_tray_icon()
        
        # Show startup notification
        tray_icon.notify(
            "OCR Agent Started", 
            "OCR Agent is now running in background.\nPress F1 for screenshot."
        )
        
        # Run tray icon
        try:
            tray_icon.run()
        except Exception as e:
            print(f"[Tray] Error running tray icon: {e}")
        finally:
            print("[Tray] System tray stopped")