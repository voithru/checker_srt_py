import os
from pathlib import Path
from collections import defaultdict
from tkinter import Tk, filedialog

# 파일명 변환 함수
def convert_srt_files_in_folder(input_dir, result_file_path):
    input_path_list = sorted(list(input_dir.glob("**/*.srt")) if input_dir.is_dir() else [])
    error_list = []
    file_count_by_lang = defaultdict(int)  # 언어별 파일 수를 저장할 딕셔너리
    changes = []

    with open(result_file_path, 'w', encoding='utf-8') as result_file:
        for input_path in input_path_list:
            try:
                lang = input_path.parent.name.lower()  # 폴더 이름을 소문자로 변환
                stem = input_path.stem

                # '.mp4' 및 '_ko' 부분 제거
                stem = stem.replace(".mp4", "").replace("_ko","")

                # '_episode' 앞의 모든 텍스트를 추출
                prefix, episode_info = stem.split("_episode", 1)

                # 에피소드 번호 추출
                episode_number = ''.join(filter(str.isdigit, episode_info.split("_", 1)[0]))
                if not episode_number:
                    raise ValueError("에피소드 번호를 찾을 수 없습니다.")
                number = int(episode_number)

                # 언어 코드 폴더명을 사용
                lang_code = lang

                new_name = f"{prefix}_episode{number:03}_subtitle{number:03}_{lang_code}.srt"
                new_path = input_path.parent / new_name
                changes.append((input_path.name, new_name))
                input_path.rename(new_path)
                file_count_by_lang[lang] += 1  # 해당 언어 폴더의 파일 수 증가
            except Exception as e:
                error_list.append(input_path.name)

        # 통계 정보 기록
        result_file.write("파일 이름 일괄 변경 완료\n")
        result_file.write(f"총 파일: {len(input_path_list)}\n")

        if error_list:
            result_file.write(f"에러가 발생한 파일: {len(error_list)}\n")
            result_file.write("\n".join(error_list) + "\n")

        result_file.write("\n언어별 파일 수정 개수:\n")
        for lang, count in file_count_by_lang.items():
            result_file.write(f"{lang}: {count}개 파일 수정\n")

        # 변경 내역 기록
        result_file.write("\n변경 내역:\n")
        for old_name, new_name in changes:
            result_file.write(f"{old_name} -> {new_name}\n")

def main():
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder Containing Subtitles")

    if not folder_path:
        print("No folder selected. Exiting...")
        return

    result_file_path = Path(folder_path) / 'result.txt'
    convert_srt_files_in_folder(Path(folder_path), result_file_path)

if __name__ == "__main__":
    main()
