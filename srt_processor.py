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
