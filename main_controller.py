from main_view import MainView

class MainController:
    def __init__(self):
        self.mainView = MainView()
        
    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        self.mainView.delete_current_rect()
            
    def on_mouse_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            self.mainView.delete_current_rect()
            self.mainView.draw_rect(self.start_x, self.start_y, event.x, event.y)
            
    def on_mouse_up(self, event):
        if self.start_x is not None and self.start_y is not None:
            # compute rect area
            end_x, end_y = event.x, event.y
            
            # compute 4 points of rect
            left = min(self.start_x, end_x)
            top = min(self.start_y, end_y)
            right = max(self.start_x, end_x)
            bottom = max(self.start_y, end_y)
            
            # check size of error
            if abs(right - left) > 5 and abs(bottom - top) > 5:
                self.selected_area = (left, top, right, bottom)
                
                # 更新提示信息
                self.canvas.create_text(
                    self.root.winfo_screenwidth()//2, 100,
                    text=f"已选择区域: {right-left}x{bottom-top} 像素\n按回车开始OCR识别，ESC取消",
                    fill='yellow',
                    font=('Arial', 14)
                )