import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from logging.handlers import RotatingFileHandler
from settings_manager import SettingsManager
from error_settings_window import ErrorSettingsWindow
from srt_processor import process_folder
import sys
import traceback
from datetime import datetime

# 로그 설정
log_folder = 'logs'
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_folder, f'srt_checker_{current_time}.log')

# 로거 생성
logger = logging.getLogger('SRTChecker')
logger.setLevel(logging.DEBUG)

# 파일 핸들러 설정 (최대 5MB, 최대 5개 백업 파일)
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)

# 콘솔 핸들러 설정
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# 포맷터 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 핸들러 추가
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 시작 로그 메시지
logger.info("Application started")

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("SRT Checker")
        self.pack(fill=tk.BOTH, expand=True)
        
        # 설정 파일 경로 설정
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(application_path, "srt_checker_settings.json")
            
        self.settings_manager = SettingsManager(self.settings_file)
        self.settings = self.settings_manager.get_settings()
        logging.debug(f"Initialized settings: {self.settings}")
        
        self.create_widgets()
        logging.info("Application initialized")

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        self.select_folder_button = ttk.Button(button_frame, text="폴더 선택", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT)

        self.settings_button = ttk.Button(button_frame, text="에러 설정", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        # 트리뷰와 스크롤바를 포함할 프레임 생성
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # 트리뷰 생성
        self.results_tree = ttk.Treeview(tree_frame)
        self.results_tree["columns"] = ("File", "StartTC", "ErrorType", "ErrorContent", "SubtitleText")
        self.results_tree.column("#0", width=100, stretch=tk.NO)
        self.results_tree.column("File", width=150, anchor=tk.W)
        self.results_tree.column("StartTC", width=100, anchor=tk.W)
        self.results_tree.column("ErrorType", width=100, anchor=tk.W)
        self.results_tree.column("ErrorContent", width=200, anchor=tk.W)
        self.results_tree.column("SubtitleText", width=300, anchor=tk.W)
        self.results_tree.heading("#0", text="Language")
        self.results_tree.heading("File", text="File")
        self.results_tree.heading("StartTC", text="Start TC")
        self.results_tree.heading("ErrorType", text="Error Type")
        self.results_tree.heading("ErrorContent", text="Error Content")
        self.results_tree.heading("SubtitleText", text="Subtitle Text")
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        # 수직 스크롤바 추가
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # 수평 스크롤바 추가
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        # 트리뷰와 스크롤바 연결
        self.results_tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.results_tree.bind("<Double-1>", self.on_double_click)

    def save_settings(self):
        try:
            logging.debug("Saving settings")
            self.settings_manager.update_settings(self.settings)
            logging.debug(f"Settings saved: {self.settings}")
        except Exception as e:
            logging.error(f"Error in save_settings: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {str(e)}")

    def select_folder(self):
        try:
            logging.debug("Folder selection initiated")
            folder_path = filedialog.askdirectory()
            if folder_path:
                logging.debug(f"Selected folder: {folder_path}")
                results = process_folder(folder_path, self.settings)
                logging.debug(f"Processing results: {results}")
                self.display_results(results)
            else:
                logging.debug("No folder selected")
        except Exception as e:
            logging.error(f"Error in select_folder: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("오류", f"폴더 선택 중 오류 발생: {str(e)}")

    def open_settings(self):
        try:
            logging.debug("Opening settings window")
            ErrorSettingsWindow(self, self.settings)
        except Exception as e:
            logging.error(f"Error in open_settings: {str(e)}")
            logging.error(traceback.format_exc())
            messagebox.showerror("오류", f"설정 창 열기 중 오류 발생: {str(e)}")

    def display_results(self, results):
        logging.debug("Displaying results")
        self.results_tree.delete(*self.results_tree.get_children())
        for lang, lang_results in results.items():
            lang_node = self.results_tree.insert("", "end", text=lang)
            for error in lang_results:
                if isinstance(error, dict):
                    values = (
                        error["File"],
                        error["StartTC"],
                        error["ErrorType"],
                        error["ErrorContent"],
                        error["SubtitleText"].replace('\n', ' ')  # 트리뷰에서는 한 줄로 표시
                    )
                    self.results_tree.insert(lang_node, "end", values=values, tags=(error["SubtitleText"],))
                elif isinstance(error, tuple):  # PARSE_ERROR 처리
                    self.results_tree.insert(lang_node, "end", values=(error[0], "", "PARSE_ERROR", error[1], ""))
        logging.debug("Results display completed")

    def on_double_click(self, event):
        item = self.results_tree.selection()[0]
        column = self.results_tree.identify_column(event.x)
        if column == '#5':  # SubtitleText 열
            text = self.results_tree.item(item, "tags")[0]  # 원본 텍스트 (줄바꿈 포함)
            self.show_full_text(text)

    def show_full_text(self, text):
        popup = tk.Toplevel(self)
        popup.title("Full Subtitle Text")
        popup.geometry("400x300")

        text_frame = ttk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
    def on_closing(self):
        logger.info("Application closing")
        self.master.destroy()

logging.basicConfig(filename='srt_checker.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')