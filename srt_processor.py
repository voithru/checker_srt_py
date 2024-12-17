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
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        lines = f.readlines()
                    
                    i = 0
                    while i < len(lines):
                        current_line = lines[i]
                        
                        # TC 라인인지 확인
                        if ' --> ' in current_line:
                            # TC 라인 끝의 공백 제거
                            cleaned_tc_line = current_line.rstrip() + '\n'
                            if cleaned_tc_line != current_line:
                                tc_modified += 1
                            modified_lines.append(cleaned_tc_line)
                            i += 1
                            continue
                        
                        modified_lines.append(current_line)
                        i += 1
                    
                    # UTF-8 without BOM으로 저장
                    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.writelines(modified_lines)
                    
                    if tc_modified > 0:
                        files_modified += 1
                        total_tc_modified += tc_modified
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue
    
    return files_modified, total_tc_modified


def check_srt_format(folder_path):
    format_errors = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    i = 0
                    while i < len(lines):
                        # 타임코드 라인 찾기
                        if ' --> ' in lines[i]:
                            # 타임코드 윗줄 체크 (index 위치에 공백라인이 있는지)
                            if i > 0 and lines[i-1].strip() == '':
                                format_errors.append({
                                    'File': file,
                                    'Line': i,
                                    'ErrorType': 'INDEX_BLANK_LINE',
                                    'ErrorContent': '타임코드 윗줄(인덱스 위치)에 불필요한 공백라인이 있습니다.',
                                    'StartTC': lines[i].strip()
                                })
                            
                            # 텍스트 영역의 불필요한 공백라인 체크
                            text_start = i + 1
                            text_end = text_start
                            
                            # 다음 타임코드나 파일 끝을 찾을 때까지 진행
                            while text_end < len(lines):
                                if text_end + 1 >= len(lines) or ' --> ' in lines[text_end + 1]:
                                    break
                                text_end += 1
                            
                            # 텍스트 영역에서 불필요한 공백라인 체크
                            text_lines = lines[text_start:text_end+1]
                            
                            # 공백 라인 개수 체크
                            blank_lines = len([line for line in text_lines if not line.strip()])
                            
                            # 공백 라인이 1개 초과인 경우에만 에러 추가
                            if blank_lines > 1:
                                format_errors.append({
                                    'File': file,
                                    'Line': text_start + 1,
                                    'ErrorType': 'TEXT_BLANK_LINE',
                                    'ErrorContent': '자막 텍스트에 불필요한 공백라인이 있습니다.',
                                    'StartTC': lines[i].strip()
                                })
                            
                            i = text_end + 1
                            continue
                        
                        i += 1
                        
                except Exception as e:
                    format_errors.append({
                        'File': file,
                        'Line': 0,
                        'ErrorType': 'FILE_ERROR',
                        'ErrorContent': f'파일 처리 중 오류 발생: {str(e)}',
                        'StartTC': ''
                    })
    
    return format_errors
