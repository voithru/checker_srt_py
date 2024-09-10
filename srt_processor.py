import os
import pysrt
import logging
from error_checker import check_errors

def process_folder(folder_path, settings):
    results = {}
    logging.debug(f"Processing folder: {folder_path}")
    logging.debug(f"Settings: {settings}")
    
    for file in os.listdir(folder_path):
        if file.lower().endswith('.srt'):
            file_path = os.path.join(folder_path, file)
            lang_code = file.split('_')[-1].split('.')[0].upper()
            logging.debug(f"Processing file: {file}, Language code: {lang_code}")
            
            active_checks = [error['name'] for error in settings['errors'] 
                             if error['languages'].get(lang_code, False)]
            logging.debug(f"Active checks for {lang_code}: {active_checks}")
            
            if active_checks:
                try:
                    srt_file = pysrt.open(file_path)
                    errors = check_errors(srt_file, lang_code, file, settings)
                    logging.debug(f"Errors found: {errors}")
                    if errors:
                        if lang_code not in results:
                            results[lang_code] = []
                        results[lang_code].extend(errors)
                except pysrt.SrtParseError as e:
                    logging.error(f"SrtParseError in file {file}: {str(e)}")
                    if 'PARSE_ERROR' not in results:
                        results['PARSE_ERROR'] = []
                    results['PARSE_ERROR'].append((file, str(e)))
                except Exception as e:
                    logging.error(f"Unexpected error processing {file}: {str(e)}")
            else:
                logging.debug(f"Skipping file {file} as no checks are active for {lang_code}")
    
    logging.debug(f"Final results: {results}")
    return results