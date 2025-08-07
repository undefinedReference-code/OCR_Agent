import sys
import os
from main_controller import MainController

def main():
    """Main function with system tray support"""
    try:
        # Check if another instance is already running
        if check_existing_instance():
            print("OCR Agent is already running. Check system tray.")
            sys.exit(0)
        
        # Create main controller
        tool = MainController()
        
        # Run application with system tray
        tool.run()
        
    except KeyboardInterrupt:
        print("\n[Main] Application interrupted by user")
    except Exception as e:
        print(f"[Main] Application failed to start: {e}")
        import traceback
        traceback.print_exc()

def check_existing_instance():
    """Check if another instance is already running"""
    import psutil
    current_pid = os.getpid()
    current_name = os.path.basename(__file__)
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if (proc.info['pid'] != current_pid and 
                proc.info['name'] == 'python.exe' and
                proc.info['cmdline'] and
                any('main.py' in arg for arg in proc.info['cmdline'])):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

if __name__ == "__main__":
    main()