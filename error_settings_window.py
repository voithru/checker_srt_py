import tkinter as tk
from tkinter import ttk, messagebox
import logging
import traceback
from logging.handlers import RotatingFileHandler
import os

class ErrorSettingsWindow(tk.Toplevel):
    def __init__(self, parent, settings):
        try:
            super().__init__(parent)
            self.parent = parent
            self.settings = settings
            self.title("에러 설정")
            self.geometry("800x600")
            logging.debug("Initializing ErrorSettingsWindow")
            self.create_widgets()
        except Exception as e:
            logging.error(f"Error initializing ErrorSettingsWindow: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("오류", f"설정 창 초기화 중 오류 발생: {str(e)}")
            self.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.lang_vars = {}

        for error in self.settings['errors']:
            error_frame = ttk.LabelFrame(scrollable_frame, text=error['name'])
            error_frame.pack(fill=tk.X, padx=5, pady=5)

            # 전체 선택/해제 체크박스
            all_var = tk.BooleanVar(value=all(error['languages'].values()))
            ttk.Checkbutton(error_frame, text="전체선택/해제", variable=all_var,
                            command=lambda e=error['name'], v=all_var: self.toggle_all(e, v)).pack(anchor=tk.W)

            # 언어별 체크박스
            lang_frame = ttk.Frame(error_frame)
            lang_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self.lang_vars[error['name']] = {}
            for lang in ['KOR', 'ENG', 'JPN', 'CHN', 'SPA', 'VIE', 'IND', 'THA']:
                var = tk.BooleanVar(value=error['languages'].get(lang, False))
                ttk.Checkbutton(lang_frame, text=lang, variable=var).pack(side=tk.LEFT)
                self.lang_vars[error['name']][lang] = var

        # 버튼
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="저장", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        logging.debug("Widgets created in ErrorSettingsWindow")

    def toggle_all(self, error_name, all_var):
        state = all_var.get()
        for lang_var in self.lang_vars[error_name].values():
            lang_var.set(state)

    def save_settings(self):
        try:
            logging.debug("Saving settings in ErrorSettingsWindow")
            at_least_one_selected = False
            for error in self.settings['errors']:
                error_name = error['name']
                for lang, var in self.lang_vars[error_name].items():
                    error['languages'][lang] = var.get()
                    if var.get():
                        at_least_one_selected = True

            if not at_least_one_selected:
                messagebox.showwarning("경고", "최소한 하나의 언어가 선택되어야 합니다.")
                return

            logging.debug(f"Saving settings: {self.settings}")
            self.parent.settings = self.settings
            self.parent.save_settings()
            self.destroy()  # 창 닫기
            messagebox.showinfo("알림", "설정이 저장되었습니다.")
            self.parent.settings = self.settings
            self.parent.save_settings()
            self.destroy()
            logging.debug("Settings saved and window closed")
        except Exception as e:
            logging.error(f"Error saving settings in ErrorSettingsWindow: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {str(e)}")
def setup_logging():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'error_settings.log')
    
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, console_handler]
    )

setup_logging()
