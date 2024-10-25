import tkinter as tk
from tkinter import ttk, messagebox
import platform
import ttkbootstrap as tb  # ttkbootstrap 추가


class ErrorSettingsWindow(tb.Toplevel):  # tb.Toplevel으로 변경
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.parent = parent
        self.settings = settings
        self.title("에러 설정")
        self.geometry("1200x600")  # 창 크기를 넓혀서 설명을 표시할 공간 확보
        self.create_widgets()
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.scroll_speed = 2  # 스크롤 속도 조절 상수

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 고정된 헤더 프레임 생성
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)

        # 컬럼 제목 추가
        ttk.Label(header_frame, text="에러 항목", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ttk.Label(header_frame, text="설명 및 예시", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ttk.Label(header_frame, text="특이사항", font=("TkDefaultFont", 14, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # 컬럼 너비 설정
        header_frame.columnconfigure(0, weight=1, minsize=180)
        header_frame.columnconfigure(1, weight=1, minsize=300)
        header_frame.columnconfigure(2, weight=1, minsize=200)

        # 스크롤 가능한 영역 생성
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = tb.Scrollbar(
            content_frame, orient="vertical", command=self.canvas.yview, bootstyle="round"
        )
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
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

        error_descriptions = {
            "줄당 자수": ("각 줄이 최대 문자 수를 초과하는지 확인합니다.", "이것은 매우매우 매우매우 매우매우 매우매우 긴 문장입니다."),
            "줄 수": ("각 자막이 허용된 최대 줄 수를 초과하는지 확인합니다.", "첫 번째 줄\n두 번째 줄\n세 번째 줄\n네 번째 줄"),
            "@@@여부": ("각 줄에 '@@@' 혹은 '＠＠＠'가 포함되어 있는지 확인합니다.", "이것은 @@@ 불명확한 발화 표기입니다."),
            "중간 말줄임표": ("각 줄에 '⋯'가 있는지 확인합니다.", "이것은⋯ 중간 말줄임표입니다."),
            "온점 말줄임표": ("각 줄에 '...'가 있는지 확인합니다.", "이것은... 온점 말줄임표입니다."),
            "온점 2,4개": ("각 줄에 '..' 또는 '....'가 있는지 있는지 확인합니다.", "이것은.. 온점 2,4개 입니다...."),
            "줄 끝 마침표": ("각 줄 끝에 '.'가 있는지 확인합니다.", "이것은 마침표입니다."),
            "하이픈 뒤 공백O": ("각 줄에 하이픈 뒤에 공백이 있는지 확인합니다.", "- 이것은 공백O입니다."),
            "하이픈 뒤 공백X": ("각 줄에 하이픈 뒤에 공백이 없는지 확인합니다.", "-이것은 공백X입니다."),
            "불필요한 공백": ("각 줄에 이중공백: '  '\n각 줄의 맨 앞, 끝: ' '\n소괄호, 중괄호, 대괄호 안쪽의 공백: '[{( ' 또는 ' )}]'", "[ 이것은 공백입니다. )"),
            "일반 물결": ("각 줄에 '~'가 있는지 확인합니다.", "이것은 ~ 물결입니다."),
            "음표 기호": ("각 줄에 '♪'가 있을 경우, 2개가 있는지 확인합니다.\n음표의 안쪽에 공백이 있는지 확인합니다.", "♪이것은 음표입니다♪"),
            "블러 기호": ("각 줄에 '○'가 있는지 확인 합니다.", "이것은 ○입니다."),
            "전각 숫자": ("각 줄에 전각 숫자가 있는지 확인합니다.", "이것은 １２３ 전각 숫자입니다."),
            "화면자막 위치": ("각 자막에 대괄호 내의 텍스트가 일반 텍스트보다 아래에 있는지 확인합니다.\n각 자막에 대괄호가 쌍으로 존재하는지 확인합니다.", "[화면자막]\n이것은 테스트입니다."),
            "중국어 따옴표 사용" : ("각 줄에 중국어 따옴표 “ ”‘’ 가 있는지 확인합니다."," “이것은 큰 따옴표입니다.”\n‘이것은 작은 따옴표 입니다.’"),
            "괄호 사용" : ("각 줄에 소괄호와 대괄호가 올바르게 전각/반각으로 사용했는지 확인합니다.","() : 반각 소괄호, （） : 전각 소괄호\n[] : 반각 대괄호,［］ : 전각 대괄호"),
            "물음표/느낌표 사용" : ("각 줄에 물음표와 느낌표가\n단독 사용시 전각\n중복 사용시 반각인지 확인합니다.","단독사용 반각물음표?\n이중사용 전각기호！？"),
            "KOR 사용" : ("각 줄에 KOR 언어가 사용되었는지 확인합니다.","This is a 한국어 텍스트"),
            "특수 아스키 문자" : ("각 줄에 <0x08>와 <0xa0>아스키코드 기호가 사용되었는지 확인합니다.","이것은 <0x08>기호입니다./n이것은 <0xa0>기호입니다.")
        }

        error_notes = {
            "줄당 자수": "KOR: 20, ENG: 42, JPN: 16, CHN: 20\nSPA: 42, VIE: 42, IND: 55, THA: 42\n\nJPN, CHN의 경우 영문자와 공백은 0.5자 취급",
            "줄 수": "3줄 까지 정상, 4줄 이상 에러 ",
            "@@@여부": "잘 들리지 않는 구간 특수기호 검색",
            "중간 말줄임표": "온점이 아닌 특수 문자",
            "온점 말줄임표": "온점(.) 정확히 3개",
            "온점 2,4개": "온점(.) 정확히 2개 또는 4개",
            "줄 끝 마침표": "JPN, CHN : '。' 과 '.' 모두 포함",
            "하이픈 뒤 공백O": "하이픈 뒤에 공백이 없어야 하는 언어 대상",
            "하이픈 뒤 공백X": "하이픈 뒤에 공백이 있어야 하는 언어 대상",
            "불필요한 공백": "",
            "일반 물결": "일반 물결 대신 틸다(～) 사용 언어 대상 (일본어)",
            "음표 기호": "",
            "블러 기호": "에러 체크 목적이 아닌, 블러기호 확인",
            "전각 숫자": "",
            "화면자막 위치": "대괄호 표기 텍스트가 일반 텍스트보다 아래에 있어야 하는 작업 대상",
            "중국어 따옴표 사용" : "",
            "괄호 사용" : "JPN : 소괄호 전각, 대괄호 반각\nCHN : 소괄호 반각, 대괄호 반각\n이 외의 언어 동작X",
            "물음표/느낌표 사용" : "소괄호, 대괄호와 같이 쓰였는지는 검사하지 않습니다.\n물음표와 느낌표의 중복 사용만 체크합니다.",
            "KOR 사용" : "한국어를 제외한 언어 대상",
            "특수 아스키 문자" : "아스키코드 <0x08>, <0xa0> 사용 여부"
        }

        for i, error in enumerate(self.settings["errors"]):
            error_frame = ttk.Frame(self.scrollable_frame)
            error_frame.grid(row=i*2, column=0, sticky="ew", padx=10, pady=(10, 0), ipadx=5, ipady=5)

            error_label = ttk.Label(
                error_frame, text=error["name"], font=("TkDefaultFont", 15, "bold")
            )
            error_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

            all_var = tk.BooleanVar(value=all(error["languages"].values()))
            ttk.Checkbutton(
                error_frame,
                text="전체선택/해제",
                variable=all_var,
                command=lambda e=error["name"], v=all_var: self.toggle_all(e, v),
            ).grid(row=0, column=1, sticky=tk.E)

            lang_frame = ttk.Frame(error_frame)
            lang_frame.grid(row=1, column=0, columnspan=2, pady=5)

            self.lang_vars[error["name"]] = {}
            for j, lang in enumerate(
                ["KOR", "ENG", "JPN", "CHN", "SPA", "VIE", "IND", "THA"]
            ):
                var = tk.BooleanVar(value=error["languages"].get(lang, False))
                ttk.Checkbutton(lang_frame, text=lang, variable=var).grid(
                    row=j // 4, column=j % 4, sticky=tk.W, padx=5, pady=2
                )
                self.lang_vars[error["name"]][lang] = var

            # 에러 설명 추가
            description, example = error_descriptions.get(error["name"], ("", ""))
            desc_label = ttk.Label(
                self.scrollable_frame, text=f"설명:\n{description}\n\n검색 텍스트 예시:\n{example}", anchor="w", justify="left"
            )
            desc_label.grid(row=i*2, column=1, sticky="w", padx=20, pady=5)

            # 특이사항 추가
            note = error_notes.get(error["name"], "")
            note_label = ttk.Label(
                self.scrollable_frame, text=f"{note}", anchor="w", justify="left"
            )
            note_label.grid(row=i*2, column=2, sticky="w", padx=20, pady=5)

            # 에러 항목과 설명 사이에 구분선 추가
            ttk.Separator(self.scrollable_frame, orient="horizontal").grid(
                row=i*2+1, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 0)
            )

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=20, fill=tk.X)

        tb.Button(button_frame, text="취소", command=self.destroy, bootstyle="danger-outline").pack(side=tk.RIGHT)
        tb.Button(button_frame, text="저장", command=self.save_settings, bootstyle="success-outline").pack(
            side=tk.RIGHT, padx=10
        )

    def _on_mousewheel(self, event):
        if not self.winfo_exists():
            return

        try:
            # 현재 스크롤 위치와 전체 크기 확인
            current_position = self.canvas.yview()

            # 스크롤 방향 결정 (방향만 사용, 크기는 무시)
            if platform.system() == "Windows":
                direction = -1 if event.delta > 0 else 1
            elif platform.system() == "Darwin":  # macOS
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
            if (delta > 0 and current_position[1] < 1.0) or \
                (delta < 0 and current_position[0] > 0.0):
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
        at_least_one_selected = False
        for error in self.settings["errors"]:
            error_name = error["name"]
            for lang, var in self.lang_vars[error_name].items():
                error["languages"][lang] = var.get()
                if var.get():
                    at_least_one_selected = True

        if not at_least_one_selected:
            messagebox.showwarning(
                "경고", "최소한 하나의 언어가 선택되어야 합니다."
            )
            return
        self.parent.settings = self.settings
        self.parent.save_settings()
        self.destroy()
        messagebox.showinfo("알림", "설정이 저장되었습니다.")

    def on_closing(self):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")
        self.destroy()