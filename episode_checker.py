import os
import pysrt
import re
from tkinter import Tk, filedialog, Button, Label
import subprocess

# 언어 코드 폴더 탐색 및 파일 읽기
language_folders = ['en', 'ja', 'zh', 'es', 'th', 'id']

expected_first_lines_patterns = {
    'en': r'\[Episode (\d+)\]',
    'zh': r'\[第(\d+)集\]',
    'ja': r'［第(\d+)話］',
    'es': r'\[Episodio (\d+)\]',
    'th': r'\[ตอนที่ (\d+)\]',
    'id': r'\[Episode (\d+)\]'
}

def read_first_subtitle_text(file_path):
    subs = pysrt.open(file_path)
    if subs and len(subs) > 0:
        first_text = subs[0].text.strip()
        first_line = first_text.split('\n')[0]
        return first_line
    return None

def extract_episode_number(file_name):
    episode_pattern = r'episode(\d+)'
    match = re.search(episode_pattern, file_name, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def is_fullwidth(char):
    return '\uFF10' <= char <= '\uFF19'

def check_subtitle_file(file_path, lang, episode_number):
    first_text = read_first_subtitle_text(file_path)
    if first_text:
        pattern = expected_first_lines_patterns.get(lang)
        if pattern:
            match = re.match(pattern, first_text)
            if match:
                first_text_episode_number = match.group(1)
                if lang == 'ja':
                    if len(first_text_episode_number) == 1:
                        # 한 자리 숫자는 전각이어야 함
                        if is_fullwidth(first_text_episode_number):
                            return False, first_text
                    else:
                        # 두 자리 이상 숫자는 반각이어야 함
                        for char in first_text_episode_number:
                            if not is_fullwidth(char):
                                return False, first_text
                return False, first_text
    return True, first_text

def main(folder_path):
    results = []
    incorrect_files = []
    for lang in language_folders:
        lang_folder_path = os.path.join(folder_path, lang)
        if os.path.exists(lang_folder_path):
            for root, dirs, files in os.walk(lang_folder_path):
                for file in files:
                    if file.endswith('.srt'):
                        file_path = os.path.join(root, file)
                        episode_number = extract_episode_number(file)
                        if episode_number is not None:
                            subtitle_check, first_text = check_subtitle_file(file_path, lang, episode_number)
                            if not subtitle_check:
                                incorrect_files.append(f"File: {file_path}, First Line: {first_text} - invalid file")
                            else:
                                results.append(f"File: {file_path}, First Line: {first_text}")
    
    result_file_path = os.path.join(os.path.dirname(__file__), "result.txt")
    with open(result_file_path, "w", encoding="utf-8") as result_file:
        if incorrect_files:
            result_file.write("The following files have issues:\n")
            for file in incorrect_files:
                result_file.write(file + "\n")
        result_file.write("\nAll file details:\n")
        for result in results:
            result_file.write(result + "\n")

    subprocess.run(["notepad.exe", result_file_path])

def select_folder():
    folder_path = filedialog.askdirectory(title="시리즈 폴더를 선택하세요")
    if folder_path:
        main(folder_path)

def run_app():
    root = Tk()
    root.title("[스푼라디오] 에피소드 체커")
    root.geometry("300x150")

    label = Label(root, text="시리즈 폴더를 선택하세요")
    label.pack(pady=20)

    select_button = Button(root, text="폴더 선택", command=select_folder)
    select_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_app()
