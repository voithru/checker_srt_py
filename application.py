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
        
        self.settings_file = self.get_settings_file_path()
        self.settings_manager = SettingsManager(self.settings_file)
        self.settings = self.settings_manager.get_settings()
        
        self.create_widgets()

    def get_settings_file_path(self):
        app_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        return os.path.join(app_dir, "srt_checker_settings.json")

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_button_frame()
        self.create_results_tree()

    def create_button_frame(self):
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        buttons = [
            ("폴더 선택", self.select_folder),
            ("에러 설정", self.open_settings),
            ("결과 저장", self.save_results_to_file)
        ]

        for text, command in buttons:
            button = ttk.Button(button_frame, text=text, command=command)
            button.pack(side=tk.LEFT, padx=(0, 5))

        self.save_results_button = button_frame.winfo_children()[-1]
        self.save_results_button.config(state=tk.DISABLED)

    def create_results_tree(self):
        tree_frame = ttk.Frame(self)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("File", "StartTC", "ErrorType", "ErrorContent", "SubtitleText")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150, anchor=tk.W)
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        self.results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.results_tree.bind("<Double-1>", self.on_double_click)

    def save_settings(self):
        try:
            self.settings_manager.update_settings(self.settings)
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {str(e)}")

    def select_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.results = process_folder(self.folder_path, self.settings)
            self.display_results(self.results)
            self.save_results_button.config(state=tk.NORMAL)

    def open_settings(self):
        ErrorSettingsWindow(self, self.settings)

    def display_results(self, results):
        self.results_tree.delete(*self.results_tree.get_children())
        for lang, lang_results in results.items():
            lang_node = self.results_tree.insert("", "end", text=lang)
            for error in lang_results:
                self.insert_error(lang_node, error)

    def insert_error(self, parent, error):
        if isinstance(error, dict):
            values = (
                error["File"],
                error["StartTC"],
                error["ErrorType"],
                error["ErrorContent"],
                error["SubtitleText"].replace('\n', ' ')
            )
            self.results_tree.insert(parent, "end", values=values, tags=(error["SubtitleText"],))
        elif isinstance(error, tuple):
            self.results_tree.insert(parent, "end", values=(error[0], "", "PARSE_ERROR", error[1], ""))

    def on_double_click(self, event):
        item = self.results_tree.selection()[0]
        values = self.results_tree.item(item, "values")
        
        # 값이 없는 경우 (언어 항목 등) 무시
        if not values:
            return

        column = self.results_tree.identify_column(event.x)
        
        actions = {
            '#1': lambda: self.open_file(values[0]),
            '#2': lambda: self.copy_start_tc_and_open_file(values[1], values[0]),
            '#5': lambda: self.show_full_text(self.results_tree.item(item, "tags")[0])
        }
        
        action = actions.get(column)
        if action:
            action()

    def copy_start_tc_and_open_file(self, start_tc, file_name):
        pyperclip.copy(start_tc)
        self.open_file(file_name)

    def show_full_text(self, text):
        popup = tk.Toplevel(self)
        popup.title("전체 자막 텍스트")
        popup.geometry("400x300")

        text_widget = tk.Text(popup, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(popup, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget.config(yscrollcommand=scrollbar.set)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
    
    def open_file(self, file_name):
        if not self.folder_path:
            messagebox.showerror("오류", "폴더가 선택되지 않았습니다.")
            return

        full_path = os.path.join(self.folder_path, file_name)
        if not os.path.exists(full_path):
            messagebox.showerror("오류", f"파일을 찾을 수 없습니다: {full_path}")
            return

        if platform.system() == 'Darwin':
            subprocess.call(('open', full_path))
        elif platform.system() == 'Windows':
            os.startfile(full_path)
        else:  # linux
            subprocess.call(('xdg-open', full_path))

    def save_results_to_file(self):
        if not self.results:
            messagebox.showinfo("알림", "저장할 결과가 없습니다.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for lang, lang_results in self.results.items():
                    f.write(f"Language: {lang}\n")
                    f.write("-" * 50 + "\n")
                    for error in lang_results:
                        if isinstance(error, dict):
                            for key, value in error.items():
                                f.write(f"{key}: {value}\n")
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