import tkinter as tk
from tkinter import ttk, messagebox
import os
import platform

class ErrorSettingsWindow(tk.Toplevel):
    def __init__(self, parent, settings):
        try:
            super().__init__(parent)
            self.parent = parent
            self.settings = settings
            self.title("에러 설정")
            self.geometry("800x600")
            self.create_widgets()
            self.resizable(True, True)
            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.scroll_speed = 2  # 스크롤 속도 조절 상수
        except Exception as e:
            messagebox.showerror("오류", f"설정 창 초기화 중 오류 발생: {str(e)}")
            self.destroy()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 마우스 휠 이벤트 바인딩
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

        self.lang_vars = {}

        for error in self.settings['errors']:
            error_frame = ttk.Frame(self.scrollable_frame)
            error_frame.pack(fill=tk.X, padx=10, pady=5, ipadx=5, ipady=5)
            
            error_label = ttk.Label(error_frame, text=error['name'], font=('TkDefaultFont', 12, 'bold'))
            error_label.pack(anchor=tk.W, pady=(0, 5))

            all_var = tk.BooleanVar(value=all(error['languages'].values()))
            ttk.Checkbutton(error_frame, text="전체선택/해제", variable=all_var,
                            command=lambda e=error['name'], v=all_var: self.toggle_all(e, v)).pack(anchor=tk.W)

            lang_frame = ttk.Frame(error_frame)
            lang_frame.pack(fill=tk.X, pady=5)
            
            self.lang_vars[error['name']] = {}
            for i, lang in enumerate(['KOR', 'ENG', 'JPN', 'CHN', 'SPA', 'VIE', 'IND', 'THA']):
                var = tk.BooleanVar(value=error['languages'].get(lang, False))
                ttk.Checkbutton(lang_frame, text=lang, variable=var).grid(row=i//4, column=i%4, sticky=tk.W, padx=5, pady=2)
                self.lang_vars[error['name']][lang] = var

            ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=20, fill=tk.X)
        
        ttk.Button(button_frame, text="취소", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="저장", command=self.save_settings).pack(side=tk.RIGHT, padx=10)

    def _on_mousewheel(self, event):
        if not self.winfo_exists():
            return
        
        try:
            # 현재 스크롤 위치와 전체 크기 확인
            current_position = self.canvas.yview()
            
            # 스크롤 방향 결정 (방향만 사용, 크기는 무시)
            if platform.system() == 'Windows':
                direction = -1 if event.delta > 0 else 1
            elif platform.system() == 'Darwin':  # macOS
                direction = -1 if event.delta < 0 else 1
            else:  # Linux
                if event.num == 4:
                    direction = -1
                elif event.num == 5:
                    direction = 1
                else:
                    return
            
            # 고정된 스크롤 양 적용
            delta = direction * self.scroll_speed
            
            # 스크롤 적용
            if (delta > 0 and current_position[1] < 1.0) or (delta < 0 and current_position[0] > 0.0):
                self.canvas.yview_scroll(int(delta), "units")
        except tk.TclError:
            # 윈도우가 이미 닫혔거나 캔버스가 존재하지 않는 경우
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")

    def toggle_all(self, error_name, all_var):
        state = all_var.get()
        for lang_var in self.lang_vars[error_name].values():
            lang_var.set(state)

    def save_settings(self):
        try:
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
            self.parent.settings = self.settings
            self.parent.save_settings()
            self.destroy()
            messagebox.showinfo("알림", "설정이 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류 발생: {str(e)}")

    def on_closing(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self.destroy()
