import unicodedata
import re


def count_cjk_characters(text):
    count = 0
    for char in text:
        # 가타카나 (반각 처리)
        if '\u30A0' <= char <= '\u30FF':  # 전각 가타카나 범위
            count += 0.5
        # 한자
        elif '\u4E00' <= char <= '\u9FFF':  # CJK 통합 한자
            count += 1
        # 히라가나
        elif '\u3040' <= char <= '\u309F':
            count += 1
        # 공백
        elif char.isspace():
            count += 0.5
        # 영문자
        elif 'a' <= char.lower() <= 'z':
            count += 0.5
        # 전각 부호
        elif unicodedata.east_asian_width(char) in ['F', 'W'] and not any([
            '\u4E00' <= char <= '\u9FFF',  # 한자
            '\u3040' <= char <= '\u309F',  # 히라가나
            '\u30A0' <= char <= '\u30FF',  # 가타카나
        ]):
            count += 1
        # 반각 부호 및 기타 문자
        else:
            count += 0.5
    
    return count


def check_errors(srt_file, lang_code, file_name, settings):
    errors = []
    error_checks = {
        "줄당 자수": check_line_length,
        "줄 수": check_line_count,
        "@@@여부": check_at_marks,
        "중간 말줄임표": check_ellipsis,
        "온점 말줄임표": check_dot_ellipsis,
        "온점 2,4개": check_double_dot,
        "줄 끝 마침표": check_end_punctuation,
        "줄 끝 마침표 누락": check_missing_end_punctuation,
        "하이픈 뒤 공백O": lambda srt, lang, fname: check_hyphen_space(
            srt, lang, fname, True
        ),
        "하이픈 뒤 공백X": lambda srt, lang, fname: check_hyphen_space(
            srt, lang, fname, False
        ),
        "불필요한 공백": check_space_errors,
        "일반 물결": check_normal_tilde,
        "음표 기호": check_music_note,
        "블러 처리 기호": check_blur_symbol,
        "전각 숫자": check_fullwidth_numbers,
        "화면자막 위치": check_bracket_text_position,
        "중국어 따옴표 사용": check_chinese_quotes,
        "괄호 사용": check_bracket_usage,
        "물음표/느낌표 사용": check_question_exclamation_usage,
        "KOR 사용": check_korean_language, 
        "특수 아스키 문자": check_special_ascii_characters,
        "하이픈 1개": check_single_hyphen,
        "대괄호 내용 오류": check_bracket_content,
        "Duration 오류": check_duration,
        "마지막 줄 쉼표": check_last_line_comma,
        "일본어 구두점": check_japanese_punctuation,
    }

    for error_check in settings["errors"]:
        if error_check["languages"].get(lang_code, False):
            check_function = error_checks.get(error_check["name"])
            if check_function:
                errors.extend(check_function(srt_file, lang_code, file_name))

    return errors


def check_line_length(srt_file, lang_code, file_name):
    errors = []
    max_lengths = {
        "KOR": 35,  # 35자까지 허용
        "ENG": 46,  # 46자까지 허용
        "JPN": 24,  # 24자까지 허용
        "CHN": 20,
        "SPA": 42,
        "VIE": 42,
        "IND": 55,
        "THA": 42,
    }
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if lang_code in ["JPN", "CHN"]:
                length = count_cjk_characters(line)
            else:
                length = len(line)
            if length > max_lengths[lang_code]:
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "줄당 자수",
                    "ErrorContent": f"{line_num}번째 줄, {length:.1f} 자 (최대: {max_lengths[lang_code]})",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_line_count(srt_file, lang_code, file_name):
    errors = []
    max_lines = 2  # 2줄까지 허용, 3줄부터 에러

    for sub in srt_file:
        lines = sub.text.split("\n")
        if len(lines) > max_lines:
            error = {
                "File": file_name,
                "StartTC": str(sub.start),
                "ErrorType": "줄 수",
                "ErrorContent": f"{len(lines)}줄 (최대: {max_lines}줄)",
                "SubtitleText": sub.text,
            }
            errors.append(error)
    return errors


def check_at_marks(srt_file, lang_code, file_name):
    errors = []
    at_marks = ['@@@', '＠＠＠']  # 골뱅이 리스트

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if any(at_mark in line for at_mark in at_marks):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "@@@여부",
                    "ErrorContent": f"{line_num}번 줄",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_ellipsis(srt_file, lang_code, file_name):
    errors = []
    ellipsis_pattern = re.compile(r"⋯")

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if ellipsis_pattern.search(line):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "중간 말줄임표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_dot_ellipsis(srt_file, lang_code, file_name):
    errors = []
    ellipsis_pattern = re.compile(r"(?<!\.)\.\.\.(?!\.)")

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if ellipsis_pattern.search(line):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "온점 말줄임표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_double_dot(srt_file, lang_code, file_name):
    errors = []
    dot_pattern = re.compile(r"(?<![.])[.]{2}(?![.])|(?<![.])[.]{4}(?![.])")

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            matches = dot_pattern.finditer(line)
            for match in matches:
                error_type = "온점 2개" if len(match.group()) == 2 else "온점 4개"
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": error_type,
                    "ErrorContent": f"{line_num}번째 줄, 위치: {match.start()}",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_end_punctuation(srt_file, lang_code, file_name):
    errors = []

    end_puncts = ["."] if lang_code not in ["JPN", "CHN"] else ["。", "."]

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if (
                line
                and any(line.endswith(punct) for punct in end_puncts)
                and not line.endswith("...")
            ):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "줄 끝 마침표",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors


def check_hyphen_space(srt_file, lang_code, file_name, space_expected):
    errors = []
    error_type = "하이픈 뒤 공백O" if space_expected else "하이픈 뒤 공백X"

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("-"):
                if space_expected:
                    if line.strip().startswith("- "):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": error_type,
                            "ErrorContent": f"{line_num}번째 줄",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
                else:
                    if not line.strip().startswith("- "):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": error_type,
                            "ErrorContent": f"{line_num}번째 줄",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
    return errors


def check_space_errors(srt_file, lang_code, file_name):
    errors = []
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if line.strip() != line:
                errors.append(
                    {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "불필요한 공백",
                        "ErrorContent": f"{line_num}번째 줄: 줄 시작/끝 공백",
                        "SubtitleText": sub.text,
                    }
                )
            if "  " in line:
                errors.append(
                    {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "불필요한 공백",
                        "ErrorContent": f"{line_num}번째 줄: 이중 공백",
                        "SubtitleText": sub.text,
                    }
                )
            if re.search(r"[\(\[\{]\s|\s[\)\]\}]", line):
                errors.append(
                    {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "불필요한 공백",
                        "ErrorContent": f"{line_num}번째 줄: 괄호 안쪽 공백",
                        "SubtitleText": sub.text,
                    }
                )

    return errors


def check_normal_tilde(srt_file, lang_code, file_name):
    errors = []
    normal_tildes = ["~", "〜"]  # 일반 물결과 일본어 물결

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for tilde in normal_tildes:
                if tilde in line:
                    positions = [i for i, char in enumerate(line) if char == tilde]
                    for pos in positions:
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": "일반 물결",
                            "ErrorContent": f"{line_num}번째 줄, 위치: {pos}, 문자: {tilde}",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
    return errors


def check_music_note(srt_file, lang_code, file_name):
    errors = []
    music_note = "♪"
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if music_note in line:
                note_count = line.count(music_note)
                if note_count != 2:
                    errors.append(
                        {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": "음표 기호 개수",
                            "ErrorContent": f"{line_num}번째 줄: \
                                한 줄에 음표 기호가 2개가 아님 (현재 {note_count}개)",
                            "SubtitleText": sub.text,
                        }
                    )
                else:
                    first_note_index = line.index(music_note)
                    second_note_index = line.rindex(music_note)
                    if (
                        first_note_index + 1 < len(line)
                        and line[first_note_index + 1] != " "
                    ):
                        errors.append(
                            {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "음표 기호 공백",
                                "ErrorContent": f"{line_num}번째 줄: 첫 번째 음표 기호 뒤에 공백 없음",
                                "SubtitleText": sub.text,
                            }
                        )

                    if second_note_index > 0 and line[second_note_index - 1] != " ":
                        errors.append(
                            {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "음표 기호 공백",
                                "ErrorContent": f"{line_num}번째 줄: 두 번째 음표 기호 앞에 공백 없음",
                                "SubtitleText": sub.text,
                            }
                        )
    return errors


def check_blur_symbol(srt_file, lang_code, file_name):
    errors = []
    blur_symbol = "○"

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if blur_symbol in line:
                positions = [i for i, char in enumerate(line) if char == blur_symbol]
                for pos in positions:
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "블러 처리 기호",
                        "ErrorContent": f"{line_num}번째 줄, 위치: {pos}",
                        "SubtitleText": sub.text,
                    }
                    errors.append(error)
    return errors


def check_fullwidth_numbers(srt_file, lang_code, file_name):
    errors = []
    fullwidth_numbers = "０１２３４５６７８９"  # 전각 숫자들

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                if char in fullwidth_numbers:
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "전각 숫자",
                        "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}",
                        "SubtitleText": sub.text,
                    }
                    errors.append(error)
    return errors


def check_bracket_text_position(srt_file, lang_code, file_name):
    errors = []

    for sub in srt_file:
        lines = sub.text.split("\n")
        bracket_lines = []
        normal_lines = []
        is_bracket_open = False
        opening_brackets = 0
        closing_brackets = 0

        for i, line in enumerate(lines):
            if "[" in line:
                is_bracket_open = True
                opening_brackets += line.count("[")
            if "]" in line:
                closing_brackets += line.count("]")
                if opening_brackets == closing_brackets:
                    is_bracket_open = False

            if is_bracket_open or "[" in line or "]" in line:
                bracket_lines.append(i)
            elif line.strip():
                normal_lines.append(i)

        if opening_brackets != closing_brackets:
            errors.append(
                {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "화면자막 대괄호 오류",
                    "ErrorContent": f"대괄호 쌍이 맞지 않습니다. (여는 대괄호: {opening_brackets}, 닫는 대괄호: {closing_brackets})",
                    "SubtitleText": sub.text,
                }
            )

        if bracket_lines and normal_lines:
            if max(normal_lines) > min(bracket_lines):
                errors.append(
                    {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "화면자막 위치 오류",
                        "ErrorContent": "일반 텍스트가 화면 텍스트보다 아래에 있습니다.",
                        "SubtitleText": sub.text,
                    }
                )

    return errors

def check_chinese_quotes(srt_file, lang_code, file_name):
    errors = []
    chinese_quotes = ['“', '”', '‘', '’']  # 중국어 큰따옴표와 작은따옴표

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for quote in chinese_quotes:
                if quote in line:
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "중국어 따옴표 사용",
                        "ErrorContent": f"{line_num}번째 줄, 위치: {line.index(quote)}, 문자: {quote}",
                        "SubtitleText": sub.text,
                    }
                    errors.append(error)
    return errors

def check_bracket_usage(srt_file, lang_code, file_name):
    errors = []
    
    # 언어별 기준 설정
    criteria = {
        "JPN": {
            "parentheses": "fullwidth",  # 소괄호는 전각이어야 함
            "brackets": "halfwidth",     # 대괄호는 반각이어야 함
        },
        "CHN": {
            "parentheses": "halfwidth",  # 소괄호는 반각이어야 함
            "brackets": "halfwidth",     # 대괄호는 반각이어야 함
        },
        # 다른 언어에 대한 기준을 여기에 추가
    }
    
    # 반각 및 전각 기호 정의
    halfwidth_parentheses = "()"
    fullwidth_parentheses = "（）"
    halfwidth_brackets = "[]"
    fullwidth_brackets = "［］"
    
    # 현재 언어의 기준 가져오기
    if lang_code not in criteria:
        return errors  # 기준이 없는 언어는 검사하지 않음
    
    current_criteria = criteria[lang_code]
    
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                if char in halfwidth_parentheses + fullwidth_parentheses:
                    expected = current_criteria["parentheses"]
                    if (char in halfwidth_parentheses and expected == "fullwidth") or \
                       (char in fullwidth_parentheses and expected == "halfwidth"):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": "소괄호 사용 오류",
                            "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
                elif char in halfwidth_brackets + fullwidth_brackets:
                    expected = current_criteria["brackets"]
                    if (char in halfwidth_brackets and expected == "fullwidth") or \
                       (char in fullwidth_brackets and expected == "halfwidth"):
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": "대괄호 사용 오류",
                            "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
    return errors


def check_question_exclamation_usage(srt_file, lang_code, file_name):
    errors = []
    halfwidth_symbols = "!?"
    fullwidth_symbols = "！？"
    question_exclamation = "!?！？"
    exception_mark = "…"

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for i, char in enumerate(line):
                if char in question_exclamation:
                    prev_char = line[i-1] if i > 0 else None
                    next_char = line[i+1] if i < len(line) - 1 else None

                    if char in halfwidth_symbols:
                        if (prev_char in fullwidth_symbols if prev_char else False) or (next_char in fullwidth_symbols if next_char else False):
                            error = {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "반각 ?! 주위 전각 ?!",
                                "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}",
                                "SubtitleText": sub.text,
                            }
                            errors.append(error)
                        elif (prev_char not in question_exclamation+exception_mark if prev_char else True) and (next_char not in question_exclamation+exception_mark if next_char else True):
                            error = {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "반각 ?! 주위 부호 없음",
                                "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}는 전각이어야 합니다.",
                                "SubtitleText": sub.text,
                            }
                            errors.append(error)
                    elif char in fullwidth_symbols:
                        if (prev_char in halfwidth_symbols if prev_char else False) or (next_char in halfwidth_symbols if next_char else False):
                            error = {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "전각 ?! 주위 반각 ?!",
                                "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}",
                                "SubtitleText": sub.text,
                            }
                            errors.append(error)
                        elif (prev_char in fullwidth_symbols if prev_char else False) or (next_char in fullwidth_symbols if next_char else False):
                            error = {
                                "File": file_name,
                                "StartTC": str(sub.start),
                                "ErrorType": "전각 ?! 주위 전각 ?!",
                                "ErrorContent": f"{line_num}번째 줄, 위치: {i}, 문자: {char}는 반각이어야 합니다.",
                                "SubtitleText": sub.text,
                            }
                            errors.append(error)

    return errors


def check_korean_language(srt_file, lang_code, file_name):
    errors = []
    if lang_code == "KOR":
        return errors  # 한국어 파일은 검사하지 않음

    korean_char_pattern = re.compile(r'[\u1100-\u11FF\u3130-\u318F\uAC00-\uD7AF]')

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if korean_char_pattern.search(line):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "KOR 사용",
                    "ErrorContent": f"{line_num}번째 줄에 한국어가 포함되어 있습니다.",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    return errors

def check_special_ascii_characters(srt_file, lang_code, file_name):
    errors = []
    special_chars = {
        '\x08': "<0x08> 문자",
        '\xA0': "<0xA0> 문자"
    }

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for char, error_type in special_chars.items():
                if char in line:
                    positions = [i for i, c in enumerate(line) if c == char]
                    for pos in positions:
                        error = {
                            "File": file_name,
                            "StartTC": str(sub.start),
                            "ErrorType": error_type,
                            "ErrorContent": f"{line_num}번째 줄, 위치: {pos}",
                            "SubtitleText": sub.text,
                        }
                        errors.append(error)
    return errors

def check_single_hyphen(srt_file, lang_code, file_name):
    errors = []
    hyphen = '-'

    for sub in srt_file:
        lines = sub.text.split("\n")
        hyphen_count = sum(line.count(hyphen) for line in lines)
        leading_hyphen_lines = [line_num for line_num, line in enumerate(lines, 1) if line.strip().startswith(hyphen)]

        if hyphen_count == 1:
            error_content = "중간 하이픈 1개"
            if leading_hyphen_lines:
                error_content = f"맨 앞 하이픈: {', '.join(map(str, leading_hyphen_lines))}번째 줄"
            
            error = {
                "File": file_name,
                "StartTC": str(sub.start),
                "ErrorType": "하이픈 개수 오류",
                "ErrorContent": error_content,
                "SubtitleText": sub.text,
            }
            errors.append(error)

    return errors

def check_bracket_content(srt_file, lang_code, file_name):
    errors = []
    bracket_pattern = re.compile(r'\[(.*?)\]')  # 대괄호 안의 내용을 찾는 정규식

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            matches = bracket_pattern.finditer(line)
            for match in matches:
                content = match.group(1)
                # 특수기호나 숫자만 있는지 확인
                if content and all(char.isdigit() or not char.isalnum() for char in content):
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "대괄호 내용 오류",
                        "ErrorContent": f"{line_num}번째 줄, 대괄호 안에 번역할 텍스트가 없습니다: '{content}'",
                        "SubtitleText": sub.text,
                    }
                    errors.append(error)

    return errors

def check_duration(srt_file, lang_code, file_name):
    errors = []
    min_duration = 1.0  # 1초
    max_duration = 8.0  # 8초

    for sub in srt_file:
        # 시작 시간을 초로 변환
        start_total_seconds = (sub.start.hours * 3600 + 
                             sub.start.minutes * 60 + 
                             sub.start.seconds + 
                             sub.start.milliseconds / 1000)
        
        # 종료 시간을 초로 변환
        end_total_seconds = (sub.end.hours * 3600 + 
                           sub.end.minutes * 60 + 
                           sub.end.seconds + 
                           sub.end.milliseconds / 1000)
        
        duration = end_total_seconds - start_total_seconds

        if duration < min_duration:
            error = {
                "File": file_name,
                "StartTC": str(sub.start),
                "ErrorType": "Duration 오류",
                "ErrorContent": f"자막 길이가 너무 짧습니다: {duration:.3f}초 (최소: {min_duration}초)",
                "SubtitleText": sub.text,
            }
            errors.append(error)
        elif duration > max_duration:
            error = {
                "File": file_name,
                "StartTC": str(sub.start),
                "ErrorType": "Duration 오류",
                "ErrorContent": f"자막 길이가 너무 깁니다: {duration:.3f}초 (최대: {max_duration}초)",
                "SubtitleText": sub.text,
            }
            errors.append(error)
    return errors

def check_missing_end_punctuation(srt_file, lang_code, file_name):
    errors = []
    # 언어별 문장 끝 부호 정의
    end_puncts = {
        "JPN": ["。", ".", "！", "？", "…"],  # 일본어
        "CHN": ["。", ".", "！", "？", "…"],  # 중국어
        "default": [".", "!", "?", "..."]     # 기타 언어
    }
    
    # 예외 처리할 특수 케이스 (마침표가 없어도 되는 경우)
    exceptions = [
        r"^\[.*\]$",  # 대괄호로 감싸진 텍스트
        r"^♪.*♪$"    # 음표 사이의 텍스트
    ]
    
    puncts = end_puncts.get(lang_code, end_puncts["default"])
    
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # 빈 줄 무시
                continue
                
            # 예외 케이스 확인
            if any(re.match(pattern, line) for pattern in exceptions):
                continue
                
            # 마지막 줄이 아닌 경우는 건너뛰기
            if line_num < len(lines) and lines[line_num].strip():
                continue
                
            # 문장 끝 부호 확인
            if not any(line.endswith(punct) for punct in puncts):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "줄 끝 마침표 누락",
                    "ErrorContent": f"{line_num}번째 줄",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    
    return errors

def check_last_line_comma(srt_file, lang_code, file_name):
    errors = []
    
    for sub in srt_file:
        lines = sub.text.split("\n")
        # 빈 줄 제거
        lines = [line for line in lines if line.strip()]
        
        if lines:  # 줄이 하나 이상 있는 경우
            last_line = lines[-1].strip()
            if last_line.endswith(","):
                error = {
                    "File": file_name,
                    "StartTC": str(sub.start),
                    "ErrorType": "마지막 줄 쉼표",
                    "ErrorContent": f"마지막 줄이 쉼표로 끝납니다",
                    "SubtitleText": sub.text,
                }
                errors.append(error)
    
    return errors

def check_japanese_punctuation(srt_file, lang_code, file_name):
    errors = []
    western_punctuation = ['.', ',']
        
    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            for punct in western_punctuation:
                if punct in line:
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "일본어 구두점",
                        "ErrorContent": f"{line_num}번째 줄: '{punct}' 사용",
                        "SubtitleText": sub.text,
                    }
                    errors.append(error)
    
    return errors