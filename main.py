import tkinter as tk
from application import Application
import sys
import os

# 실행 파일의 디렉토리를 sys.path에 추가
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(application_path)

def main():
    root = tk.Tk()
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()