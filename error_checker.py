import unicodedata
import logging
import re

logger = logging.getLogger('SRTChecker')

def count_cjk_characters(text):
    count = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ['F', 'W']:
            count += 1
        elif unicodedata.east_asian_width(char) in ['Na', 'H'] or char.isspace():
            count += 0.5
        else:
            count += 1
    return count

def check_errors(srt_file, lang_code, file_name, settings):
    errors = []
    for error_check in settings['errors']:
        if error_check['languages'].get(lang_code, False):
            logging.debug(f"Checking {error_check['name']} for {lang_code}")
            if error_check['name'] == "줄당 자수":
                errors.extend(check_line_length(srt_file, lang_code, file_name))
            elif error_check['name'] == "줄 수":
                errors.extend(check_line_count(srt_file, lang_code, file_name))
            elif error_check['name'] == "???여부":
                errors.extend(check_question_marks(srt_file, lang_code, file_name))
            elif error_check['name'] == "중간 말줄임표":
                errors.extend(check_ellipsis(srt_file, lang_code, file_name))
            elif error_check['name'] == "온점 말줄임표":
                errors.extend(check_dot_ellipsis(srt_file, lang_code, file_name))
            elif error_check['name'] == "줄 끝 마침표":
                errors.extend(check_end_punctuation(srt_file, lang_code, file_name))
            elif error_check['name'] == "하이픈 뒤 공백O":
                errors.extend(check_hyphen_space(srt_file, lang_code, file_name, True))
            elif error_check['name'] == "하이픈 뒤 공백X":
                errors.extend(check_hyphen_space(srt_file, lang_code, file_name, False))
    return errors

def check_line_length(srt_file, lang_code, file_name):
    errors = []
    max_lengths = {
        'KOR': 20, 'ENG': 42, 'JPN': 16, 'CHN': 20,
        'SPA': 42, 'VIE': 42, 'IND': 55, 'THA': 42
    }
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            if lang_code in ['JPN', 'CHN']:
                length = count_cjk_characters(line)
            else:
                length = len(line)
            
            if length > max_lengths[lang_code]:
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "줄당 자수",
                    "ErrorContent": f"{line_num}번째 줄, {length:.1f} 자 (최대: {max_lengths[lang_code]})",
                    "SubtitleText": sub.text
                }
                errors.append(error)
    return errors

def check_line_count(srt_file, lang_code, file_name):
    errors = []
    max_lines = 2  # 최대 줄 수를 2로 설정
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        if len(lines) > max_lines:
            error = {
                "File": file_name,
                "StartTC": str(sub.start),
                "ErrorType": "줄 수",
                "ErrorContent": f"{len(lines)}줄 (최대: {max_lines}줄)",
                "SubtitleText": sub.text
            }
            errors.append(error)
            logging.debug(f"Line count error in {file_name}: {error}")
    return errors

def check_question_marks(srt_file, lang_code, file_name):
    errors = []
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            if '???' in line:
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "???여부",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text
                }
                errors.append(error)
                logging.debug(f"??? found in {file_name}: {error}")
    return errors

def check_ellipsis(srt_file, lang_code, file_name):
    errors = []
    ellipsis_pattern = re.compile(r'⋯')
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            if ellipsis_pattern.search(line):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "중간 말줄임표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text
                }
                errors.append(error)
                logging.debug(f"Incorrect ellipsis found in {file_name}: {error}")
    return errors


def check_dot_ellipsis(srt_file, lang_code, file_name):
    errors = []
    ellipsis_pattern = re.compile(r'\.\.\.')
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            if ellipsis_pattern.search(line):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "온점 말줄임표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text
                }
                errors.append(error)
                logging.debug(f"Incorrect ellipsis found in {file_name}: {error}")
    return errors

def check_end_punctuation(srt_file, lang_code, file_name):
    errors = []
    
    end_puncts = ['.'] if lang_code not in ['JPN', 'CHN'] else ['。', '.']
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()  # 앞뒤 공백 제거
            if line and any(line.endswith(punct) for punct in end_puncts):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "줄 끝 마침표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text
                }
                errors.append(error)
                logging.debug(f"Missing end punctuation in {file_name}: {error}")
    return errors

def check_hyphen_space(srt_file, lang_code, file_name, space_expected):
    errors = []
    error_type = "하이픈 뒤 공백O" if space_expected else "하이픈 뒤 공백X"
    
    for sub in srt_file:
        lines = sub.text.split('\n')
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('-'):
                if space_expected:
                    if line.strip().startswith('- '):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": error_type,
                            "ErrorContent": f"{line_num}번째 줄",
                            "SubtitleText": sub.text
                        }
                        errors.append(error)
                        logger.debug(f"Hyphen space error in {file_name}: {error}")
                else:
                    if not line.strip().startswith('- '):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": error_type,
                            "ErrorContent": f"{line_num}번째 줄",
                            "SubtitleText": sub.text
                        }
                        errors.append(error)
                        logger.debug(f"Hyphen space error in {file_name}: {error}")
    return errors

logging.basicConfig(level=logging.DEBUG)