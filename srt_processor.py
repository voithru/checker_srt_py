import os
import pysrt
from error_checker import check_errors


def process_folder(folder_path, settings):
    results = {}

    for file in os.listdir(folder_path):
        if file.lower().endswith(".srt"):
            file_path = os.path.join(folder_path, file)
            lang_code = file.split("_")[-1].split(".")[0].upper()

            active_checks = [
                error["name"]
                for error in settings["errors"]
                if error["languages"].get(lang_code, False)
            ]

            if active_checks:
                try:
                    srt_file = pysrt.open(file_path)
                    errors = check_errors(srt_file, lang_code, file, settings)
                    if errors:
                        if lang_code not in results:
                            results[lang_code] = []
                        results[lang_code].extend(errors)
                except pysrt.SrtParseError as e:
                    if "PARSE_ERROR" not in results:
                        results["PARSE_ERROR"] = []
                    results["PARSE_ERROR"].append((file, str(e)))

    return results
