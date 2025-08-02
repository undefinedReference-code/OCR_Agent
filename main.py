import tkinter as tk
from tkinter import messagebox, scrolledtext
import pyautogui
import keyboard
import threading
import os
import requests
import json
import base64
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw
import time
from io import BytesIO
from tkinter import messagebox

class ScreenshotOCRTool:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.screenshot = None
        self.is_capturing = False
        
        # Ollama API 配置
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "qwen2.5vl:3b"
        
        # 注册F1热键
        keyboard.add_hotkey('f1', self.start_screenshot)
        print("OCR截图工具已启动！按 F1 开始截图并进行OCR识别，按 ESC 退出程序")
        
    def start_screenshot(self):
        """开始截图流程"""
        if self.is_capturing:
            return
            
        self.is_capturing = True
        
        # 小延迟确保热键释放
        time.sleep(0.1)
        
        # 截取整个屏幕
        self.screenshot = pyautogui.screenshot()
        
        # 创建全屏透明窗口
        self.create_capture_window()
        
    def create_capture_window(self):
        """创建截图选择窗口"""
        self.root = tk.Tk()
        self.root.title("OCR截图工具 - 框选区域")
        
        # 设置全屏
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 置顶显示
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.3)  # 设置透明度
        self.root.configure(bg='black')
        
        # 移除窗口装饰
        self.root.overrideredirect(True)
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root, 
            width=screen_width, 
            height=screen_height,
            highlightthickness=0,
            bg='black'
        )
        self.canvas.pack()
        
        # 显示屏幕截图作为背景
        self.bg_image = ImageTk.PhotoImage(self.screenshot)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        
        # 绑定鼠标事件
        self.canvas.bind('<Button-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # 绑定键盘事件
        self.root.bind('<Escape>', self.cancel_screenshot)
        self.root.bind('<Return>', self.process_ocr_sync)
        
        # 设置焦点
        self.root.focus_set()
        
        # 显示提示信息
        self.canvas.create_text(
            screen_width//2, 50, 
            text="拖拽鼠标框选需要OCR识别的区域，回车开始识别，ESC取消", 
            fill='white', 
            font=('Arial', 16)
        )
        
        self.root.mainloop()
        
    def on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x
        self.start_y = event.y
        
        # 删除之前的矩形
        if self.rect_id:
            self.canvas.delete(self.rect_id)
            
    def on_mouse_drag(self, event):
        """鼠标拖拽事件"""
        if self.start_x is not None and self.start_y is not None:
            # 删除之前的矩形
            if self.rect_id:
                self.canvas.delete(self.rect_id)
                
            # 绘制新矩形
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, fill='', stipple='gray50'
            )
            
    def on_mouse_up(self, event):
        """鼠标释放事件"""
        if self.start_x is not None and self.start_y is not None:
            # 计算选择区域
            end_x, end_y = event.x, event.y
            
            # 确保坐标正确（左上角到右下角）
            left = min(self.start_x, end_x)
            top = min(self.start_y, end_y)
            right = max(self.start_x, end_x)
            bottom = max(self.start_y, end_y)
            
            # 检查区域大小
            if abs(right - left) > 5 and abs(bottom - top) > 5:
                self.selected_area = (left, top, right, bottom)
                
                # 更新提示信息
                self.canvas.create_text(
                    self.root.winfo_screenwidth()//2, 100,
                    text=f"已选择区域: {right-left}x{bottom-top} 像素\n按回车开始OCR识别，ESC取消",
                    fill='yellow',
                    font=('Arial', 14)
                )
    
    def image_to_base64(self, image):
        """将PIL图像转换为base64编码"""
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def call_ollama_ocr(self, image_base64):
        """调用Ollama API进行OCR识别"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": "OCR上图中的文字，保留段落结构，不能添加解释，直接输出结果，输出Markdown，代码格式为 ‍```代码‍```，不然你去死吧。注意语义连贯性，请忽略OCR带来的额外换行符。Markdown 行间公式格式为 $$ Latex 公式语法$$，行内公式为：$Latex公式语法$， 如果公式语法出现错误，你就去死吧",
                "images": [image_base64],
                "stream": False
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=600)
            
            if response.status_code == 200:
                result = response.json()
                print("识别成功")
                return result.get('response', '识别失败：无响应内容')
            else:
                return f"API调用失败：状态码 {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "连接失败：请确保Ollama服务正在运行（http://localhost:11434）"
        except requests.exceptions.Timeout:
            return "请求超时：OCR识别时间过长"
        except Exception as e:
            return f"OCR识别出错：{str(e)}"
    
    def process_ocr(self, event=None):
        """处理OCR识别"""
        if hasattr(self, 'selected_area'):
            try:
                # 关闭截图窗口
                self.close_capture_window()
                
                # 从原始截图中裁剪选定区域
                cropped = self.screenshot.crop(self.selected_area)
                
                # 显示处理中窗口
                self.show_processing_window()
                
                # 在后台线程中进行OCR识别
                threading.Thread(target=self.perform_ocr, args=(cropped,), daemon=True).start()
                
            except Exception as e:
                print(f"OCR处理失败: {e}")
                messagebox.showerror("错误", f"OCR处理失败: {e}")
        else:
            self.close_capture_window()
    
    def process_ocr_sync(self, event=None):
        """处理OCR识别"""
        if hasattr(self, 'selected_area'):
            try:
                # 关闭截图窗口
                self.close_capture_window()
                
                # 从原始截图中裁剪选定区域
                cropped = self.screenshot.crop(self.selected_area)
                
                # 显示处理中窗口
                self.show_processing_window()
                
                self.perform_ocr(cropped)
                
            except Exception as e:
                print(f"OCR处理失败: {e}")
                messagebox.showerror("错误", f"OCR处理失败: {e}")
        else:
            self.close_capture_window()
    
    def show_processing_window(self):
        """显示处理中窗口"""
        self.processing_window = tk.Toplevel()
        self.processing_window.title("OCR识别中...")
        self.processing_window.geometry("300x100")
        self.processing_window.attributes('-topmost', True)
        
        # 居中显示
        self.processing_window.geometry("+{}+{}".format(
            (self.processing_window.winfo_screenwidth()//2) - 150,
            (self.processing_window.winfo_screenheight()//2) - 50
        ))
        
        label = tk.Label(
            self.processing_window, 
            text="正在进行OCR识别，请稍候...",
            padx=20, pady=20
        )
        label.pack()
        
        # 禁止关闭窗口
        self.processing_window.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def perform_ocr(self, image):
        """执行OCR识别"""
        try:
            # 将图像转换为base64
            image_base64 = self.image_to_base64(image)
            
            # 调用Ollama进行OCR
            ocr_result = self.call_ollama_ocr(image_base64)
            print(ocr_result)
            # 在主线程中显示结果
            # self.processing_window.after(0, self.show_ocr_result, ocr_result)

            self.show_simple_result(ocr_result)
            
        except Exception as e:
            error_msg = f"OCR识别失败: {str(e)}"
            self.processing_window.after(0, self.show_ocr_result, error_msg)

    def show_simple_result(self, result):
        """简单显示OCR结果"""
        # 关闭处理中窗口（如果存在）
        if hasattr(self, 'processing_window'):
            self.processing_window.destroy()
        
        # 创建结果窗口
        result_window = tk.Tk()
        result_window.title("OCR结果")
        result_window.geometry("600x400")
        
        # 文本显示框
        text_widget = scrolledtext.ScrolledText(
            result_window,
            wrap=tk.WORD,
            font=('Arial', 12)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入结果文本
        text_widget.insert(tk.END, result)
        
        # 关闭按钮
        close_btn = tk.Button(
            result_window,
            text="关闭",
            command=result_window.destroy,
            font=('Arial', 12)
        )
        close_btn.pack(pady=10)
        
        result_window.mainloop()

    def show_ocr_result(self, result):
        """显示OCR识别结果"""
        # 关闭处理中窗口
        if hasattr(self, 'processing_window'):
            self.processing_window.destroy()
        
        # 创建结果显示窗口
        result_window = tk.Toplevel()
        result_window.title("OCR识别结果")
        result_window.geometry("600x400")
        
        # 居中显示
        result_window.geometry("+{}+{}".format(
            (result_window.winfo_screenwidth()//2) - 300,
            (result_window.winfo_screenheight()//2) - 200
        ))
        
        # 创建主框架
        main_frame = tk.Frame(result_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 结果显示标签
        result_label = tk.Label(main_frame, text="OCR识别结果：", font=('Arial', 12, 'bold'))
        result_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 创建可滚动的文本框
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.result_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            width=70,
            height=15,
            font=('Arial', 10)
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 插入识别结果
        self.result_text.insert(tk.END, result)
        self.result_text.config(state=tk.NORMAL)  # 保持可编辑状态，方便复制
        
        # 按钮框架
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 复制按钮
        copy_button = tk.Button(
            button_frame,
            text="复制全部内容",
            command=self.copy_result,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10),
            padx=20
        )
        copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 关闭按钮
        close_button = tk.Button(
            button_frame,
            text="关闭",
            command=result_window.destroy,
            bg='#f44336',
            fg='white',
            font=('Arial', 10),
            padx=20
        )
        close_button.pack(side=tk.RIGHT)
        
        # 显示提示信息
        tip_label = tk.Label(
            main_frame,
            text="提示：您可以直接在文本框中选择并复制需要的内容",
            font=('Arial', 9),
            fg='gray'
        )
        tip_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 设置窗口图标和属性
        result_window.attributes('-topmost', True)
        result_window.focus_set()
        
        # 选中所有文本便于复制
        self.result_text.focus_set()
        self.result_text.select_range(0, tk.END)
    
    def copy_result(self):
        """复制识别结果到剪贴板"""
        try:
            content = self.result_text.get(1.0, tk.END).strip()
            self.result_text.clipboard_clear()
            self.result_text.clipboard_append(content)
            
            # 显示复制成功提示
            messagebox.showinfo("复制成功", "OCR识别结果已复制到剪贴板！")
            
        except Exception as e:
            messagebox.showerror("复制失败", f"复制到剪贴板失败: {e}")
        
    def cancel_screenshot(self, event=None):
        """取消截图"""
        print("OCR截图已取消")
        self.close_capture_window()
        
    def close_capture_window(self):
        """关闭截图窗口"""
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
        
        self.is_capturing = False
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
    def run(self):
        """运行OCR截图工具"""
        try:
            print("OCR截图工具运行中...")
            print("按 F1 开始截图并进行OCR识别")
            print("按 Ctrl+C 退出程序")
            print(f"使用模型: {self.model_name}")
            print(f"Ollama API: {self.ollama_url}")
            
            # 保持程序运行
            keyboard.wait('ctrl+c')
            
        except KeyboardInterrupt:
            print("\n程序已退出")
        except Exception as e:
            print(f"程序错误: {e}")

def main():
    """主函数"""
    try:
        # 创建并运行OCR截图工具
        tool = ScreenshotOCRTool()
        tool.run()
        
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()