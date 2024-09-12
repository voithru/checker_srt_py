import tkinter as tk
from application import Application
import sys
from pathlib import Path

def setup_environment():
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 실행 파일인 경우
        application_path = Path(sys._MEIPASS)
    else:
        # 스크립트로 실행되는 경우
        application_path = Path(__file__).parent
    
    # 애플리케이션 경로를 시스템 경로에 추가
    sys.path.append(str(application_path))

def main():
    setup_environment()
    
    root = tk.Tk()
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()