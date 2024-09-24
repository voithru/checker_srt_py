import json
import os
import sys

class SettingsManager:
    def __init__(self, settings_file):
        self.settings_file = self.get_settings_file_path(settings_file)
        self.settings = self.load_settings()

    def get_settings_file_path(self, settings_file):
        if getattr(sys, 'frozen', False):
            # PyInstaller로 빌드된 실행 파일인 경우
            application_path = os.path.dirname(sys.executable)
        else:
            # 스크립트로 실행되는 경우
            application_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(application_path, settings_file)

    def load_settings(self):
        default_languages = {
            lang: True for lang in ['KOR', 'ENG', 'JPN', 'CHN', 'SPA', 'VIE', 'IND', 'THA']}
        default_settings = {
            "errors": [
                {"name": "줄당 자수", "languages": default_languages.copy()},
                {"name": "줄 수", "languages": default_languages.copy()},
                {"name": "@@@여부", "languages": default_languages.copy()},
                {"name": "중간 말줄임표", "languages": {
                    "KOR": True,
                    "ENG": False,
                    "JPN": False,
                    "CHN": False,
                    "SPA": False,
                    "VIE": False,
                    "IND": False,
                    "THA": False}},
                {"name": "온점 말줄임표", "languages": {
                    "KOR": False,
                    "ENG": True,
                    "JPN": True,
                    "CHN": True,
                    "SPA": True,
                    "VIE": True,
                    "IND": True,
                    "THA": True}},
                {"name": "온점 2,4개", "languages": default_languages.copy()},
                {"name": "줄 끝 마침표", "languages": {
                    "KOR": True,
                    "ENG": True,
                    "JPN": True,
                    "CHN": True,
                    "SPA": False,
                    "VIE": True,
                    "IND": False,
                    "THA": True}},
                {"name": "하이픈 뒤 공백O", "languages": {
                    "KOR": False,
                    "ENG": True,
                    "JPN": False,
                    "CHN": False,
                    "SPA": False,
                    "VIE": False,
                    "IND": True,
                    "THA": False}},
                {"name": "하이픈 뒤 공백X", "languages": {
                    "KOR": True,
                    "ENG": False,
                    "JPN": True,
                    "CHN": True,
                    "SPA": True,
                    "VIE": True,
                    "IND": False,
                    "THA": True}},
                {"name": "불필요한 공백", "languages": default_languages.copy()},
                {"name": "일반 물결", "languages": {
                    "KOR": False,
                    "ENG": False,
                    "JPN": True,
                    "CHN": False,
                    "SPA": False,
                    "VIE": False,
                    "IND": False,
                    "THA": False}},
                {"name": "음표 기호", "languages": default_languages.copy()},
                {"name": "블러 기호", "languages": default_languages.copy()},
                {"name": "전각 숫자", "languages": default_languages.copy()},
                {"name": "화면자막 위치", "languages": default_languages.copy()},
                {"name": "중국어 따옴표 사용", "languages": {
                    "KOR": False,
                    "ENG": False,
                    "JPN": False,
                    "CHN": True,
                    "SPA": False,
                    "VIE": False,
                    "IND": False,
                    "THA": False}
                 },
                 {"name": "괄호 사용", "languages": {
                    "KOR": False,
                    "ENG": False,
                    "JPN": True,
                    "CHN": True,
                    "SPA": False,
                    "VIE": False,
                    "IND": False,
                    "THA": False}
                 },
                 {"name": "물음표/느낌표 사용", "languages": {
                    "KOR": False,
                    "ENG": False,
                    "JPN": True,
                    "CHN": True,
                    "SPA": False,
                    "VIE": False,
                    "IND": False,
                    "THA": False}
                 },
                 {"name": "KOR 사용", "languages": default_languages.copy()},
            ]
        }
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                return loaded_settings
            except json.JSONDecodeError:
                return default_settings
        else:
            return default_settings

    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"설정 저장 중 오류 발생: {str(e)}")
            raise

    def get_settings(self):
        return self.settings

    def update_settings(self, new_settings):
        self.settings = new_settings
        self.save_settings()
