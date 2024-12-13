import os
import pysrt
from error_checker import check_errors


def process_folder(folder_path, settings):
    results = {}

    for file in os.listdir(folder_path):
        if file.lower().endswith(".srt"):
            file_path = os.path.join(folder_path, file)
            lang_code = file.split("_")[-1].split(".")[0].upper()

            srt_file = pysrt.open(file_path)
            errors = check_errors(srt_file, lang_code, file, settings)
            if errors:
                if lang_code not in results:
                    results[lang_code] = []
                results[lang_code].extend(errors)

    return results


def remove_end_tc_spaces(folder_path):
    files_modified = 0
    total_tc_modified = 0
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = os.path.join(root, file)
                tc_modified = 0
                modified_lines = []
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    i = 0
                    while i < len(lines):
                        current_line = lines[i]
                        
                        # 현재 줄이 숫자만 있는지 확인 (자막 번호)
                        if current_line.strip().isdigit():
                            # 다음 줄이 존재하고 TC 라인인지 확인
                            if i + 1 < len(lines) and ' --> ' in lines[i + 1]:
                                tc_line = lines[i + 1]
                                # TC 라인 끝의 공백 제거
                                cleaned_tc_line = tc_line.rstrip() + '\n'
                                if cleaned_tc_line != tc_line:
                                    tc_modified += 1
                                modified_lines.append(current_line)
                                modified_lines.append(cleaned_tc_line)
                                i += 2  # TC 라인까지 처리했으므로 2줄 건너뛰기
                                continue
                        
                        # TC 라인이 아닌 경우 그대로 추가
                        modified_lines.append(current_line)
                        i += 1
                    
                    # 모든 파일을 UTF-8로 저장 (변경사항 유무와 관계없이)
                    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.writelines(modified_lines)
                    
                    if tc_modified > 0:
                        files_modified += 1
                        total_tc_modified += tc_modified
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue
    
    return files_modified, total_tc_modified
