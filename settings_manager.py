import json
import os
import logging

import logging
import os
import json

class SettingsManager:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.settings = self.load_settings()

    def load_settings(self):
        default_languages = {lang: True for lang in ['KOR', 'ENG', 'JPN', 'CHN', 'SPA', 'VIE', 'IND', 'THA']}
        default_settings = {
            "errors": [
                {"name": "줄당 자수", "languages": default_languages.copy()},
                {"name": "줄 수", "languages": default_languages.copy()},
                {"name": "???여부", "languages": default_languages.copy()},
                {"name": "중간 말줄임표", "languages": {"KOR": True, "ENG": False, "JPN": False, "CHN": False, "SPA": False, "VIE": False, "IND": False, "THA": False}},
                {"name": "온점 말줄임표", "languages": {"KOR": False, "ENG": True, "JPN": True, "CHN": True, "SPA": True, "VIE": True, "IND": True, "THA": True}},
                {"name": "줄 끝 마침표", "languages": {"KOR": True, "ENG": True, "JPN": True, "CHN": True, "SPA": False, "VIE": True, "IND": True, "THA": True}},
                {"name": "하이픈 뒤 공백O", "languages": {"KOR": False, "ENG": True, "JPN": False, "CHN": False, "SPA": False, "VIE": False, "IND": False, "THA": False}},
                {"name": "하이픈 뒤 공백X", "languages": {"KOR": True, "ENG": False, "JPN": True, "CHN": True, "SPA": True, "VIE": True, "IND": True, "THA": True}},
                {"name": "불필요한 공백", "languages": {"KOR": True, "ENG": True, "JPN": True, "CHN": True, "SPA": True, "VIE": True, "IND": True, "THA": True}}
            ]
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                logging.debug(f"Loaded settings from file: {loaded_settings}")
                return loaded_settings
            except json.JSONDecodeError:
                logging.error(f"Failed to load settings from {self.settings_file}. Using default settings.")
                return default_settings
        else:
            logging.debug("Settings file not found. Using default settings.")
            return default_settings

    def save_settings(self):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
        logging.debug(f"Saved settings: {self.settings}")

    def get_settings(self):
        return self.settings

    def update_settings(self, new_settings):
        self.settings = new_settings
        self.save_settings()
logging.basicConfig(level=logging.DEBUG)