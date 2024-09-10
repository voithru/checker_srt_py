import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from settings_manager import SettingsManager
from error_settings_window import ErrorSettingsWindow
from srt_processor import process_folder
import sys
import traceback

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("SRT Checker")
        self.pack(fill=tk.BOTH, expand=True)
        
        # 설정 파일 경로 설정
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(application_path, "srt_checker_settings.json")
        
        self.settings_manager = SettingsManager(self.settings_file)
        self.settings = self.settings_manager.get_settings()
        logging.debug(f"Initialized settings: {self.settings}")
        
        self.create_widgets()

    def create_widgets(self):
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=10, fill=tk.X)

        self.select_folder_button = ttk.Button(button_frame, text="폴더 선택", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT)

        self.settings_button = ttk.Button(button_frame, text="에러 설정", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.results_tree = ttk.Treeview(self)
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
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # self.scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.results_tree.yview)
        # self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        # self.results_tree.configure(yscrollcommand=self.scrollbar_y.set)

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

logging.basicConfig(filename='srt_checker.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')