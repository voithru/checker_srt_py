import unicodedata
import re


def count_cjk_characters(text):
    count = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ["F", "W"]:
            count += 1
        elif unicodedata.east_asian_width(char) in ["Na", "H"] or char.isspace():
            count += 0.5
        else:
            count += 1
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
        "KOR": 20,
        "ENG": 42,
        "JPN": 16,
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
    max_lines = 3

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
    normal_tilde = "~"

    for sub in srt_file:
        lines = sub.text.split("\n")
        for line_num, line in enumerate(lines, 1):
            if normal_tilde in line:
                positions = [i for i, char in enumerate(line) if char == normal_tilde]
                for pos in positions:
                    error = {
                        "File": file_name,
                        "StartTC": str(sub.start),
                        "ErrorType": "일반 물결",
                        "ErrorContent": f"{line_num}번째 줄, 위치: {pos}",
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
                        elif (prev_char not in question_exclamation if prev_char else True) and (next_char not in question_exclamation if next_char else True):
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
