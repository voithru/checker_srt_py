import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from settings_manager import SettingsManager
from error_settings_window import ErrorSettingsWindow
from srt_processor import process_folder
import sys
import subprocess
import platform
import pyperclip

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("SRT Checker")
        self.pack(fill=tk.BOTH, expand=True)
        self.results = None
        self.folder_path = None
        
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(application_path, "srt_checker_settings.json")
            
        self.settings_manager = SettingsManager(self.settings_file)
        self.settings = self.settings_manager.get_settings()
        
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        self.select_folder_button = ttk.Button(button_frame, text="폴더 선택", command=self.select_folder)
        self.select_folder_button.pack(side=tk.LEFT)

        self.settings_button = ttk.Button(button_frame, text="에러 설정", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)

        self.save_results_button = ttk.Button(button_frame, text="결과 저장", command=self.save_results_to_file)
        self.save_results_button.pack(side=tk.LEFT, padx=5)
        self.save_results_button.config(state=tk.DISABLED)

        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

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
            self.settings_manager.update_settings(self.settings)
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {str(e)}")

    def select_folder(self):
        try:
            self.folder_path = filedialog.askdirectory()
            if self.folder_path:
                self.results = process_folder(self.folder_path, self.settings)
                self.display_results(self.results)
                self.save_results_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("오류", f"폴더 선택되지 않음: {str(e)}")
        except Exception as e:
            messagebox.showerror("오류", f"폴더 선택 중 오류 발생: {str(e)}")

    def open_settings(self):
        try:
            ErrorSettingsWindow(self, self.settings)
        except Exception as e:
            messagebox.showerror("오류", f"설정 창 열기 중 오류 발생: {str(e)}")

    def display_results(self, results):
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
                        error["SubtitleText"].replace('\n', ' ')
                    )
                    self.results_tree.insert(lang_node, "end", values=values, tags=(error["SubtitleText"],))
                elif isinstance(error, tuple):
                    self.results_tree.insert(lang_node, "end", values=(error[0], "", "PARSE_ERROR", error[1], ""))

    def on_double_click(self, event):
        item = self.results_tree.selection()[0]
        column = self.results_tree.identify_column(event.x)
        values = self.results_tree.item(item, "values")
        file_name = values[0]
        
        if column == '#1':  # File 열
            self.open_file(file_name)
        elif column == '#2':  # StartTC 열
            start_tc = values[1]
            self.copy_start_tc_and_open_file(start_tc, file_name)
        elif column == '#5':  # SubtitleText 열 (기존 기능 유지)
            text = self.results_tree.item(item, "tags")[0]
            self.show_full_text(text)

    def copy_start_tc_and_open_file(self, start_tc, file_name):
        pyperclip.copy(start_tc)
        self.open_file(file_name)

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

        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
    
    def open_file(self, file_name):
        if self.folder_path:
            full_path = os.path.join(self.folder_path, file_name)
            if os.path.exists(full_path):
                if platform.system() == 'Darwin':
                    subprocess.call(('open', full_path))
                elif platform.system() == 'Windows':
                    os.startfile(full_path)
                else:  # linux
                    subprocess.call(('xdg-open', full_path))
            else:
                messagebox.showerror("오류", f"파일을 찾을 수 없습니다: {full_path}")
        else:
            messagebox.showerror("오류", "폴더가 선택되지 않았습니다.")

    def save_results_to_file(self):
        if not self.results:
            messagebox.showinfo("알림", "저장할 결과가 없습니다.")
            return

        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                     filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not file_path:
                return

            with open(file_path, 'w', encoding='utf-8') as f:
                for lang, lang_results in self.results.items():
                    f.write(f"Language: {lang}\n")
                    f.write("-" * 50 + "\n")
                    for error in lang_results:
                        if isinstance(error, dict):
                            f.write(f"File: {error['File']}\n")
                            f.write(f"Start TC: {error['StartTC']}\n")
                            f.write(f"Error Type: {error['ErrorType']}\n")
                            f.write(f"Error Content: {error['ErrorContent']}\n")
                            f.write(f"Subtitle Text: {error['SubtitleText']}\n")
                        elif isinstance(error, tuple):
                            f.write(f"File: {error[0]}\n")
                            f.write(f"Error: PARSE_ERROR\n")
                            f.write(f"Details: {error[1]}\n")
                        f.write("-" * 50 + "\n")
            messagebox.showinfo("알림", f"결과가 {file_path}에 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"결과 저장 중 오류 발생: {str(e)}")
    def on_closing(self):
        self.master.destroy()