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


def fix_srt_format(folder_path):
    files_modified = 0
    total_tc_modified = 0
    total_text_space_modified = 0
    total_blank_lines_removed = 0
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = os.path.join(root, file)
                tc_modified = 0
                text_space_modified = 0
                blank_lines_removed = 0
                modified_lines = []
                
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        lines = f.readlines()
                    
                    i = 0
                    while i < len(lines):
                        current_line = lines[i]  # rstrip() 제거
                        
                        # 현재 줄이 숫자이고 다음 줄이 타임코드인 경우 인덱스로 판단
                        if (current_line.strip().isdigit() and 
                            i + 1 < len(lines) and 
                            ' --> ' in lines[i + 1]):
                            modified_lines.append(current_line.strip() + '\n')
                            i += 1
                            continue
                            
                        # TC 라인 처리
                        if ' --> ' in current_line:
                            # TC 라인 끝의 공백 제거
                            cleaned_tc = current_line.rstrip()
                            if cleaned_tc != current_line.rstrip('\n'):
                                tc_modified += 1
                            modified_lines.append(cleaned_tc + '\n')
                            
                            # 자막 텍스트 영역 처리
                            i += 1
                            text_lines = []
                            consecutive_blank_lines = 0
                            while i < len(lines):
                                line = lines[i]  # 원본 라인 유지
                                if not line.strip():  # 빈 줄을 만나면
                                    consecutive_blank_lines += 1
                                    i += 1
                                    # 다음 줄이 숫자이고 그 다음 줄이 타임코드면 현재 자막 블록 종료
                                    if (i < len(lines) - 1 and 
                                        lines[i].strip().isdigit() and 
                                        ' --> ' in lines[i + 1]):
                                        if consecutive_blank_lines > 1:
                                            blank_lines_removed += (consecutive_blank_lines - 1)
                                        break
                                    continue
                                
                                # 텍스트 라인 사이의 불필요한 빈 줄 카운트
                                if consecutive_blank_lines > 0:
                                    blank_lines_removed += consecutive_blank_lines
                                consecutive_blank_lines = 0
                                
                                # 텍스트 라인의 앞뒤 공백 제거 (전각/반각 모두)
                                original_line = line.rstrip('\n')  # 줄바꿈만 제거한 원본
                                cleaned_text = original_line.strip(' 　')  # 반각/전각 스페이스 모두 제거
                                if cleaned_text != original_line:  # 원본과 비교
                                    text_space_modified += 1
                                text_lines.append(cleaned_text + '\n')
                                i += 1
                            
                            # 텍스트 라인들 추가
                            modified_lines.extend(text_lines)
                            modified_lines.append('\n')  # 자막 블록 구분용 빈 줄
                            continue
                        
                        i += 1
                    
                    # 파일 끝의 불필요한 공백 라인 제거
                    while modified_lines and modified_lines[-1].strip() == '':
                        modified_lines.pop()
                    
                    # 무조건 파일 저장
                    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                        f.writelines(modified_lines)
                    
                    # 실제 수정이 발생한 경우에만 files_modified 증가
                    if tc_modified > 0 or text_space_modified > 0 or blank_lines_removed > 0:
                        files_modified += 1
                    total_tc_modified += tc_modified
                    total_text_space_modified += text_space_modified
                    total_blank_lines_removed += blank_lines_removed
                
                except Exception as e:
                    print(f"Error processing file {file_path}: {str(e)}")
                    continue
    
    return files_modified, total_tc_modified, total_text_space_modified, total_blank_lines_removed


def check_srt_format(folder_path):
    format_errors = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.srt'):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    first_tc_found = False
                    i = 0
                    while i < len(lines):
                        # 타임코드 라인 찾기
                        if ' --> ' in lines[i]:
                            # 첫 번째 타임코드가 아닐 경우에만 체크
                            if first_tc_found:
                                # 타임코드 바로 윗줄이 숫자가 아니거나
                                # 그 윗줄이 빈 줄이 아닌 경우 에러
                                if (i < 1 or not lines[i-1].strip().isdigit() or 
                                    i < 2 or lines[i-2].strip() != ''):
                                    format_errors.append({
                                        'File': file,
                                        'Line': i + 1,
                                        'ErrorType': 'INDEX_BLANK_LINE',
                                        'ErrorContent': '타임코드 윗줄이 인덱스가 아니거나, 인덱스 윗줄에 빈 줄이 없습니다.',
                                        'StartTC': lines[i].strip()
                                    })
                            else:
                                # 첫 번째 타임코드는 윗줄이 인덱스인지만 체크
                                if i < 1 or not lines[i-1].strip().isdigit():
                                    format_errors.append({
                                        'File': file,
                                        'Line': i + 1,
                                        'ErrorType': 'INDEX_LINE',
                                        'ErrorContent': '타임코드 윗줄이 인덱스가 아닙니다.',
                                        'StartTC': lines[i].strip()
                                    })
                                first_tc_found = True
                        
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
