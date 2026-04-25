import locale
import json
import pathlib
from typing import Dict, Any, Optional

# Private cache to avoid repeated disk reads
_translations_cache: Dict[str, Dict[str, str]] = {}

def _get_locales_dir() -> pathlib.Path:
    """Returns the absolute path to the locales directory."""
    # Using resolve() to ensure we have the absolute physical path
    return pathlib.Path(__file__).parent.resolve() / "locales"

def _load_language_file(lang: str) -> Dict[str, str]:
    """Loads a translation JSON file from disk into the cache."""
    if lang in _translations_cache:
        return _translations_cache[lang]
    
    locales_dir = _get_locales_dir()
    file_path = locales_dir / f"{lang}.json"
    
    if not file_path.exists():
        # If the file doesn't exist, we fallback to English
        if lang == "en":
            return {}
        return _load_language_file("en")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            translations = json.load(f)
            _translations_cache[lang] = translations
            return translations
    except (json.JSONDecodeError, OSError):
        # On error, fallback to English or return empty dict
        if lang != "en":
            return _load_language_file("en")
        return {}

def get_system_language() -> str:
    """Detects system language using modern locale API, defaults to English."""
    try:
        lang_code, _ = locale.getlocale()
        if not lang_code:
            lang_code = locale.getdefaultlocale()[0]
            
        if lang_code and lang_code.startswith("es"):
            return "es"
    except Exception:
        pass
    return "en"

def resolve_language(language_setting: str) -> str:
    """Resolves 'auto' setting to actual system language."""
    if language_setting == "auto":
        return get_system_language()
    return language_setting

def translate(key: str, lang: str = "en", **kwargs) -> str:
    """Returns the translated string for a given key with fallback to English."""
    # 1. Load target language translations
    translations = _load_language_file(lang)
    
    # 2. Try to get the key from the target language
    text_template = translations.get(key)
    
    # 3. Fallback logic
    if text_template is None:
        # If missing in target language, try English cache (or load it)
        en_translations = _load_language_file("en")
        text_template = en_translations.get(key, key)
        
    try:
        # Ensure it's a string before calling format
        return str(text_template).format(**kwargs)
    except (KeyError, ValueError, IndexError):
        # If formatting fails, return the template as is
        return str(text_template)
