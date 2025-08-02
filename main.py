from main_controller import MainController

def main():
    """main function"""
    try:
        tool = MainController()
        tool.run()
        
    except Exception as e:
        print(f"init failed: {e}")

if __name__ == "__main__":
    main()